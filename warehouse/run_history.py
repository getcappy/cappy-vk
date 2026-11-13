"""Keep a separate local record of each warehouse run beside its inputs and SQL."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import mkdtemp

from settings import DATABASE

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"


class Run:
    def __init__(self, path):
        self.path = path

    def event(self, event, **values):
        record = {
            "at": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **values,
        }
        with (self.path / "events.jsonl").open("a", encoding="utf-8") as out:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    def execute(self, cursor, week, table, template, **params):
        sql = (
            (self.path / "inputs" / template)
            .read_text()
            .format(week=week, table=table, **params)
        )
        filename = f"week_{week:02d}-{table}.sql"
        (self.path / filename).write_text(sql.rstrip().removesuffix(";") + ";\n")
        self.event("sql_submitted", file=filename, table=table, week=week)
        cursor.execute(sql)
        self.event("sql_completed", file=filename)


@contextmanager
def record_run(operation, files, **scope):
    RUNS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = Path(mkdtemp(prefix=f"{stamp}-{operation}-", dir=RUNS))
    run = Run(path)
    print(f"Warehouse run: {path}", flush=True)
    run.event("started", operation=operation, database=DATABASE, **scope)
    try:
        inputs = path / "inputs"
        inputs.mkdir()
        for name in dict.fromkeys(
            ("source.json", "schema.sql", "settings.py", "run_history.py", *files)
        ):
            (inputs / name).write_bytes((ROOT / name).read_bytes())
        yield run
    except BaseException as exc:
        run.event("failed", error_type=type(exc).__name__)
        raise
    else:
        run.event("completed")
