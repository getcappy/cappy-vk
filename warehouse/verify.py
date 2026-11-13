"""Independently compute operating metrics from the source Parquet and reconcile Doris."""

import argparse
import hashlib
import json
import tempfile
import time
from pathlib import Path

import duckdb

from build import WEEKS
from run_history import ROOT, record_run
from settings import connection

MEASURES = (
    "exposures",
    "positive_watches",
    "watch_seconds",
    "watches_10s",
    "observed_completions",
    "measurable_completions",
    "likes",
    "dislikes",
    "shares",
    "bookmarks",
    "author_clicks",
    "comment_opens",
)


def reference(source, inputs=ROOT):
    manifest = json.loads((inputs / "source.json").read_text())
    for name, entry in manifest["files"].items():
        with (source / name).open("rb") as f:
            if hashlib.file_digest(f, "sha256").hexdigest() != entry["sha256"]:
                raise ValueError(f"SHA-256 mismatch: {name}")
    with duckdb.connect() as local:
        local.execute("SET threads=6")
        local.execute("SET memory_limit='10GB'")
        local.execute(
            "CREATE TEMP TABLE item AS SELECT item_id, duration FROM read_parquet(?)",
            [str(source / "items_metadata.parquet")],
        )
        weekly = []
        for week in range(3):
            path = str(source / f"week_{week:02d}.parquet")
            # Source row number is zero-based in DuckDB. Doris reserves 1 for the first exposure.
            local.execute(
                "CREATE OR REPLACE TEMP TABLE events AS SELECT e.*, i.duration FROM "
                "read_parquet(?, file_row_number=true) e LEFT JOIN item i USING (item_id)",
                [path],
            )
            row = local.execute("""
                SELECT COUNT(*), COUNT(*) FILTER (WHERE timespent > 0), SUM(timespent),
                       COUNT(*) FILTER (WHERE timespent >= 10),
                       COUNT(*) FILTER (WHERE duration BETWEEN 1 AND 254 AND timespent >= duration),
                       COUNT(*) FILTER (WHERE duration BETWEEN 1 AND 254),
                       SUM("like"::INT), SUM(dislike::INT), SUM(share::INT), SUM(bookmark::INT),
                       SUM(click_on_author::INT), SUM(open_comments::INT) FROM events""").fetchone()
            weekly.append(row)
            insert = (
                "CREATE TEMP TABLE source_week AS "
                if week == 0
                else "INSERT INTO source_week "
            )
            local.execute(
                insert
                + """SELECT ?::INT AS week_no, user_id, COUNT(*) AS exposures,
                          COUNT(*) FILTER (WHERE timespent >= 10) AS standard_views,
                          COUNT(*) FILTER (WHERE timespent >= 10 OR
                              (duration BETWEEN 1 AND 9 AND timespent >= duration)) AS expanded_views,
                          COUNT(*) FILTER (WHERE bookmark) AS bookmarks,
                          BOOL_OR(click_on_author) AS visited_author, BOOL_OR(share) AS shared, BOOL_OR(dislike) AS disliked,
                          MIN(file_row_number) FILTER (WHERE timespent >= 10) AS first_watch,
                          MAX(file_row_number) FILTER (WHERE bookmark) AS last_bookmark
                          FROM events GROUP BY user_id""",
                [week],
            )
            if week == 1:
                bands = local.execute("""SELECT CASE WHEN duration BETWEEN 1 AND 9 THEN '01-09'
                            WHEN duration BETWEEN 10 AND 29 THEN '10-29' WHEN duration BETWEEN 30 AND 59 THEN '30-59'
                            WHEN duration BETWEEN 60 AND 254 THEN '60-254' ELSE 'outside_measurement' END AS band,
                            COUNT(*), COUNT(*) FILTER (WHERE duration BETWEEN 1 AND 254 AND timespent >= duration),
                            COUNT(*) FILTER (WHERE duration BETWEEN 1 AND 254), COUNT(*) FILTER (WHERE bookmark)
                            FROM events GROUP BY band ORDER BY band""").fetchall()
                sentinels = local.execute("""SELECT file_row_number+1, user_id, item_id, place, platform, agent,
                            timespent, "like", dislike, share, bookmark, click_on_author, open_comments
                            FROM events WHERE file_row_number IN (0, 524287, 524288, 1048575, 104792374)
                            ORDER BY file_row_number""").fetchall()
            print(f"Parquet week {week}: reconciler scanned {row[0]} rows", flush=True)
        local.execute(
            "CREATE TEMP TABLE cohort AS " + (inputs / "reference.sql").read_text()
        )
        cohort = local.execute("""SELECT count(*) FILTER (WHERE standard_views >= 3),
                            count(*) FILTER (WHERE standard_views >= 3 AND future_bookmarks > 0),
                            count(*), count(*) FILTER (WHERE future_bookmarks > 0),
                            count(*) FILTER (WHERE standard_views < 3),
                            count(*) FILTER (WHERE standard_views < 3 AND future_bookmarks > 0) FROM cohort""").fetchone()
        example = local.execute("""SELECT user_id, standard_views, expanded_views, future_bookmarks FROM cohort
                 WHERE standard_views < 3 AND future_bookmarks > 0 ORDER BY user_id LIMIT 1""").fetchone()
        overlap = local.execute("""SELECT count(*) FILTER (WHERE standard_views >= 3),
                  count(*) FILTER (WHERE bookmarks > 0), count(*) FILTER (WHERE standard_views >= 3 AND bookmarks > 0),
                  count(*) FILTER (WHERE standard_views >= 3 AND bookmarks = 0),
                  count(*) FILTER (WHERE standard_views < 3 AND bookmarks > 0) FROM source_week WHERE week_no=1""").fetchone()
        retention = local.execute("""WITH masks AS (SELECT user_id, bit_or(1 << week_no) AS m
                  FROM source_week GROUP BY user_id) SELECT COUNT(*), COUNT(*) FILTER (WHERE m&1=1),
                  COUNT(*) FILTER (WHERE m&3=3), COUNT(*) FILTER (WHERE m&5=5),
                  COUNT(*) FILTER (WHERE m=7) FROM masks""").fetchone()
        funnel = local.execute("""SELECT COUNT(*), COUNT(first_watch), COUNT(*) FILTER (WHERE last_bookmark>first_watch)
                            FROM source_week WHERE week_no=1""").fetchone()
        users_per_week = local.execute(
            "SELECT COUNT(*) FROM source_week GROUP BY week_no ORDER BY week_no"
        ).fetchall()
        tags = local.execute("""SELECT week_no, COUNT(*) FILTER (WHERE visited_author),
                              COUNT(*) FILTER (WHERE bookmarks>0), COUNT(*) FILTER (WHERE standard_views>=3),
                              COUNT(*) FILTER (WHERE disliked), COUNT(*), COUNT(*) FILTER (WHERE shared)
                              FROM source_week GROUP BY week_no ORDER BY week_no""").fetchall()
        return json.loads(
            json.dumps(
                dict(
                    weekly=weekly,
                    tags=tags,
                    bands=bands,
                    sentinels=sentinels,
                    cohort=cohort,
                    example=example,
                    overlap=overlap,
                    retention=retention,
                    funnel=funnel,
                    users_per_week=users_per_week,
                )
            )
        )


def equality(actual, expected, metric):
    if actual != expected:
        raise ValueError(f"{metric}: Doris={actual}, source={expected}")


def doris(ref, inputs=ROOT):
    results = {}
    with connection() as db, db.cursor() as q:
        q.execute("SET query_timeout=1200")
        for name, key in (
            ("cohort", "cohort"),
            ("overlap", "overlap"),
            ("retention", "retention"),
            ("ordered_funnel", "funnel"),
        ):
            start = time.perf_counter()
            q.execute((inputs / (name + ".sql")).read_text())
            observed = q.fetchone()
            expected = ref[key][1:] if name == "retention" else ref[key]
            row = list(map(int, observed[: len(expected)]))
            equality(row, expected, name)
            if name == "cohort":
                for pos in (0, 2, 4):
                    ratio = float(observed[6 + pos // 2])
                    equality(
                        round(100 * expected[pos + 1] / expected[pos], 4),
                        ratio,
                        "cohort rate",
                    )
                    row.append(ratio)
            results[name] = dict(zip((c[0] for c in q.description), row))
            print(f"Doris {name}: {time.perf_counter() - start:.2f}s", flush=True)
        q.execute((inputs / "content_performance.sql").read_text())
        bands = [
            [
                r[0],
                *map(int, r[1:5]),
                *(float(v) if v is not None else None for v in r[5:]),
            ]
            for r in q.fetchall()
        ]
        equality([b[:5] for b in bands], ref["bands"], "content performance")
        for (
            band,
            exposures,
            completed,
            measurable,
            bookmarks,
            completion_pct,
            bookmark_pct,
        ) in bands:
            equality(
                completion_pct,
                round(100 * completed / measurable, 4) if measurable else None,
                band,
            )
            equality(
                bookmark_pct,
                round(100 * bookmarks / exposures, 4) if exposures else None,
                band,
            )
        results["content_performance_w1"] = [
            dict(zip((c[0] for c in q.description), r)) for r in bands
        ]
        q.execute(
            "SELECT BITMAP_UNION_COUNT(members) FROM ads_vk_user_tag_week WHERE tag_code='reached' AND rule_version=1"
        )
        results["observed_users_3w"] = q.fetchone()[0]
        equality(
            results["observed_users_3w"],
            ref["retention"][0],
            "three-week distinct users",
        )
        q.execute("""SELECT week_no, tag_code, BITMAP_COUNT(members) FROM ads_vk_user_tag_week
                      WHERE rule_version=1 ORDER BY week_no, tag_code""")
        tags = (
            "author_visitor",
            "bookmarked",
            "deep_viewer",
            "negative_feedback",
            "reached",
            "shared",
        )
        expected_tags = [
            [w, tag, count]
            for w, *counts in ref["tags"]
            for tag, count in zip(tags, counts)
        ]
        equality(
            [list(r) for r in q.fetchall()],
            expected_tags,
            "all version-1 tag populations",
        )
        weekly = ref["weekly"]
        for table in ("dws_vk_user_week", "dws_vk_video_week"):
            aggregates = ", ".join(f"SUM({m})" for m in MEASURES)
            q.execute(
                f"SELECT {aggregates} FROM {table} GROUP BY week_no ORDER BY week_no"
            )
            equality([list(map(int, r)) for r in q.fetchall()], weekly, table)
        q.execute(
            "SELECT COUNT(*) FROM dws_vk_user_week GROUP BY week_no ORDER BY week_no"
        )
        equality(
            [list(r) for r in q.fetchall()], ref["users_per_week"], "weekly user grain"
        )
        q.execute(
            "SELECT COUNT(*) FROM dws_vk_video_week GROUP BY week_no ORDER BY week_no"
        )
        videos = [r[0] for r in q.fetchall()]
        results["weeks"] = [
            dict(
                week_no=w,
                users=ref["users_per_week"][w][0],
                videos=videos[w],
                **dict(zip(MEASURES, row)),
            )
            for w, row in enumerate(weekly)
        ]
        for table in ("ods_vk_interactions", "dwd_vk_video_exposure"):
            q.execute(f"SELECT COUNT(*) FROM {table} GROUP BY week_no ORDER BY week_no")
            equality([r[0] for r in q.fetchall()], list(WEEKS), table)
        q.execute("""SELECT source_row_no,user_id,item_id,place_code,platform_code,agent_code,watch_seconds,
                         liked,disliked,shared,bookmarked,clicked_author,opened_comments FROM dwd_vk_video_exposure
                         WHERE week_no=1 AND source_row_no IN (1,524288,524289,1048576,104792375) ORDER BY source_row_no""")
        equality(
            [list(r) for r in q.fetchall()],
            ref["sentinels"],
            "source order and feedback values",
        )
        if ref["example"]:
            uid, a, b, converted = ref["example"]
            q.execute(
                """SELECT week_no, SUM(IF(watch_seconds>=10,1,0)),
                                SUM(IF(duration_seconds BETWEEN 1 AND 9 AND watch_seconds<10 AND observed_complete,1,0)),
                                SUM(IF(bookmarked,1,0)) FROM dwd_vk_video_exposure
                         WHERE user_id=%s GROUP BY week_no ORDER BY week_no""",
                (uid,),
            )
            rows = {r[0]: r[1:] for r in q.fetchall()}
            equality(
                [rows[0][2], *rows[1], rows[2][2]],
                [0, a, b - a, 0, converted],
                "individual trace",
            )
            results["example_added_and_converted"] = dict(
                user_id=uid,
                w1_standard_views=a,
                w1_expanded_views=b,
                w2_bookmarks=converted,
            )
    results["source_revision"] = json.loads((inputs / "source.json").read_text())[
        "revision"
    ]
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    files = (
        "verify.py",
        "build.py",
        "reference.sql",
        "retention.sql",
        "ordered_funnel.sql",
        "cohort.sql",
        "overlap.sql",
        "content_performance.sql",
    )
    with record_run("verify", files) as record:
        inputs = record.path / "inputs"
        results = doris(reference(args.source, inputs), inputs)
        snapshot = json.dumps(results, ensure_ascii=False, indent=2) + "\n"
        (record.path / "verified.json").write_text(snapshot)
        # Replace the convenience copy atomically, even when two checks finish together.

        with tempfile.NamedTemporaryFile(mode="w", dir=ROOT, delete=False) as out:
            out.write(snapshot)
        Path(out.name).replace(ROOT / "verified.json")
        record.event(
            "reconciled",
            weeks=len(results["weeks"]),
            observed_users=results["observed_users_3w"],
        )
        print(json.dumps(results, ensure_ascii=False))
