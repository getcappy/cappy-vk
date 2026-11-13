"""Atomically load a SHA-256-pinned source file into its ODS table or week partition."""

import argparse
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import requests

from run_history import record_run

from settings import DATABASE, connection


def write_payload(source_file, output, week):
    first = 1
    writer = None
    try:
        for batch in source_file.iter_batches(batch_size=524288):
            arrays = {}
            for name, col in zip(batch.schema.names, batch.columns):
                if col.null_count:
                    raise ValueError(f"Unexpected null in {name}")
                if pa.types.is_uint32(col.type):
                    col = col.cast(pa.int32())
                elif pa.types.is_uint8(col.type):
                    col = col.cast(pa.int16())
                arrays[name] = col
            if week is not None:
                arrays = {
                    "week_no": pa.repeat(pa.scalar(week, type=pa.int8()), len(batch)),
                    "user_id": arrays.pop("user_id"),
                    "item_id": arrays.pop("item_id"),
                    "source_row_no": pa.array(
                        np.arange(first, first + len(batch), dtype=np.int64)
                    ),
                    **arrays,
                }
            table = pa.table(arrays)
            if writer is None:
                writer = pq.ParquetWriter(output, table.schema, compression="snappy")
            writer.write_table(table)
            first += len(batch)
    finally:
        if writer:
            writer.close()
    if first - 1 != source_file.metadata.num_rows:
        raise ValueError("The payload row count differs from the source")


def send(url, auth, headers, payload, expected):
    for attempt in range(5):
        try:
            with payload.open("rb") as stream:
                response = requests.put(
                    url,
                    data=stream,
                    headers=headers,
                    auth=auth,
                    allow_redirects=False,
                    timeout=(10, 1805),
                )
            response.raise_for_status()
            body = response.json()
            receipt = {
                k: body[k]
                for k in (
                    "Status",
                    "TxnId",
                    "NumberLoadedRows",
                    "NumberFilteredRows",
                    "ExistingJobStatus",
                )
                if k in body
            }
            status = body["Status"]
            if status == "Success":
                if (
                    int(body["NumberLoadedRows"]) != expected
                    or int(body["NumberFilteredRows"]) != 0
                ):
                    raise ValueError(f"Stream Load row mismatch: {body}")
                return receipt
            if (
                status == "Label Already Exists"
                and body.get("ExistingJobStatus") == "FINISHED"
            ):
                return receipt
            if status == "Publish Timeout":
                return receipt
            if (
                status != "Label Already Exists"
                or body.get("ExistingJobStatus") != "RUNNING"
            ):
                raise ValueError(f"Stream Load failed: {body}")
        except (requests.Timeout, requests.ConnectionError):
            if attempt == 4:
                raise
        time.sleep(2**attempt)
    raise RuntimeError(f"Could not confirm Stream Load {headers['label']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("file")
    args = parser.parse_args()
    with record_run("load", ("load_parquet.py",), source_file=args.file) as record:
        load(args, record)


def load(args, record):
    manifest = json.loads((record.path / "inputs" / "source.json").read_text())
    entry = manifest["files"][args.file]
    path = args.source / args.file
    with path.open("rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != entry["sha256"]:
            raise ValueError(f"SHA-256 differs from the pinned original: {args.file}")
    source_file = pq.ParquetFile(path)
    expected = source_file.metadata.num_rows
    week = None
    if args.file.startswith("week_"):
        table = "ods_vk_interactions"
        week = int(args.file[5:7])
    else:
        table = {
            "users_metadata.parquet": "ods_vk_users",
            "items_metadata.parquet": "ods_vk_items",
        }[args.file]
    query = f"SELECT COUNT(*) FROM {table}" + (
        f" WHERE week_no={week}" if week is not None else ""
    )
    with connection() as db, db.cursor() as cursor:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        record.event(
            "source_checked",
            table=table,
            week=week,
            sha256=entry["sha256"],
            source_rows=expected,
            previous_rows=count,
        )
        if count == expected:
            record.event("already_loaded", rows=count)
            print(f"{args.file}: already loaded ({count} rows)", flush=True)
            return
        if count:
            raise ValueError(f"ODS contains {count} unexpected rows for {args.file}")
        endpoint = os.environ["VK_DORIS_BE_URL"].rstrip("/")
        url = f"{endpoint}/api/{DATABASE}/{table}/_stream_load"
        auth = os.environ["VK_DORIS_USER"], os.environ["VK_DORIS_PASSWORD"]
        headers = {
            "label": f"vk_{table}_{entry['sha256']}",
            "format": "parquet",
            "strict_mode": "true",
            "max_filter_ratio": "0",
            "Expect": "100-continue",
            "timeout": "1800",
        }
        with tempfile.TemporaryDirectory() as temp:
            payload = Path(temp) / "load.parquet"
            write_payload(source_file, payload, week)
            record.event("stream_load_submitted", label=headers["label"], table=table)
            receipt = send(url, auth, headers, payload, expected)
            record.event("stream_load_response", label=headers["label"], **receipt)
        for _ in range(60):
            cursor.execute(query)
            if cursor.fetchone()[0] == expected:
                record.event("load_verified", table=table, rows=expected)
                print(f"{args.file}: {expected} rows", flush=True)
                return
            time.sleep(2)
        raise RuntimeError(
            f"Stream Load was not visible with the expected count for {args.file}"
        )


if __name__ == "__main__":
    main()
