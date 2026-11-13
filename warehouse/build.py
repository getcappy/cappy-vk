"""Rebuild the three-week detail fact, two weekly aggregates and the audience mart."""

import argparse

from run_history import record_run
from settings import connection

WEEKS = (85_386_270, 104_792_375, 108_511_774)
GRAINS = (("dws_vk_user_week", "user_id"), ("dws_vk_video_week", "item_id"))


def run(weeks):
    weeks = list(weeks)
    inputs = ("build.py", "detail.sql", "aggregate_week.sql", "materialize_bitmaps.sql")
    with (
        record_run("build", inputs, weeks=weeks) as record,
        connection() as db,
        db.cursor() as cur,
    ):
        cur.execute("SET query_timeout=1500")
        for table, key, expected in (
            ("ods_vk_items", "item_id", 19_627_601),
            ("ods_vk_users", "user_id", 10_000_000),
        ):
            cur.execute(f"SELECT COUNT(*), COUNT(DISTINCT {key}) FROM {table}")
            rows, keys = cur.fetchone()
            record.event(
                "dimension_counts",
                table=table,
                rows=rows,
                distinct_keys=keys,
                expected=expected,
            )
            if (rows, keys) != (expected, expected):
                raise ValueError(f"Missing or duplicate dimension keys in {table}")
        for week in weeks:
            expected = WEEKS[week]
            cur.execute(
                "SELECT COUNT(*) FROM ods_vk_interactions WHERE week_no=%s", (week,)
            )
            rows = cur.fetchone()[0]
            record.event("source_week", week=week, rows=rows, expected=expected)
            if rows != expected:
                raise ValueError(f"ODS week {week} differs from the pinned snapshot")
            record.execute(cur, week, "dwd_vk_video_exposure", "detail.sql")
            cur.execute(
                """SELECT COUNT(*), COUNT(author_id), MIN(source_row_no), MAX(source_row_no),
                          BITMAP_UNION_COUNT(TO_BITMAP(source_row_no))
                          FROM dwd_vk_video_exposure WHERE week_no=%s""",
                (week,),
            )
            observed = cur.fetchone()
            record.event(
                "detail_counts",
                week=week,
                rows=observed[0],
                matched_videos=observed[1],
                first_row=observed[2],
                last_row=observed[3],
                distinct_rows=observed[4],
            )
            if observed != (expected, expected, 1, expected, expected):
                raise ValueError(
                    f"Week {week}: detail grain or video dimension coverage differs: {observed}"
                )
            print(f"Week {week}: validated {expected} detail rows", flush=True)
            for table, entity in GRAINS:
                record.execute(cur, week, table, "aggregate_week.sql", entity=entity)
                cur.execute(
                    f"SELECT SUM(exposures), COUNT(*) FROM {table} WHERE week_no=%s",
                    (week,),
                )
                exposures, keys = cur.fetchone()
                record.event(
                    "aggregate_counts",
                    week=week,
                    table=table,
                    exposures=int(exposures),
                    rows=keys,
                )
                if exposures != expected:
                    raise ValueError(
                        f"Week {week}: {table} covers {exposures} of {expected} exposures"
                    )
                print(f"Week {week}: {table} has {keys} rows", flush=True)
            cur.execute(
                """SELECT COUNT(*) FROM dws_vk_user_week w
                          LEFT ANTI JOIN dim_vk_user u ON w.user_id=u.user_id WHERE w.week_no=%s""",
                (week,),
            )
            missing_users = cur.fetchone()[0]
            record.event("missing_user_dimension", week=week, rows=missing_users)
            if missing_users:
                raise ValueError(f"Week {week} has users without a dimension record")
            record.execute(cur, week, "ads_vk_user_tag_week", "materialize_bitmaps.sql")
            cur.execute(
                "SELECT COUNT(*) FROM ads_vk_user_tag_week WHERE week_no=%s", (week,)
            )
            tags = cur.fetchone()[0]
            record.event("tag_count", week=week, rows=tags)
            if tags != 6:
                raise ValueError(f"Week {week} needs six v1 tag sets")
            print(f"Week {week}: six audience tags published", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", type=int, choices=range(len(WEEKS)))
    selected = parser.parse_args().week
    run(range(len(WEEKS)) if selected is None else [selected])
