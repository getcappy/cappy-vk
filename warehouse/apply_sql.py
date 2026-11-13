"""Apply a warehouse schema or migration file and preserve the submitted SQL."""

import argparse
from pathlib import Path

from pymysql.constants import CLIENT

from settings import connection
from run_history import record_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--bootstrap", action="store_true", help="Connect before selecting the demo database")
    args = parser.parse_args()
    with record_run("ddl", ("apply_sql.py", "build.py"), file=args.file.name) as record:
        batch = args.file.read_bytes()
        (record.path / "executed.sql").write_bytes(batch)
        # Doris parses statement boundaries, including semicolons inside comments or strings.
        with (
            connection(client_flag=CLIENT.MULTI_STATEMENTS, select_database=not args.bootstrap) as db,
            db.cursor() as cursor,
        ):
            record.event("batch_submitted", file="executed.sql")
            cursor.execute(batch.decode("utf-8"))
            index = 1
            while True:
                record.event("statement_completed", index=index)
                if not cursor.nextset():
                    break
                index += 1


if __name__ == "__main__":
    main()
