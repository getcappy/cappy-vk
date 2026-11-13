"""Prepare the three-week VK-LSVD warehouse from its pinned public source."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import requests

from run_history import ROOT, record_run

STEPS = ("download", "schema", "load", "etl", "verify")


def download(source, manifest):
    source.mkdir(parents=True, exist_ok=True)
    base = "https://huggingface.co/datasets/deepvk/VK-LSVD/resolve/" + manifest["revision"]
    with record_run("download", ("prepare.py",)) as record:
        for name, entry in manifest["files"].items():
            path = source / name
            if path.is_file() and path.stat().st_size == entry["size"]:
                with path.open("rb") as f:
                    cached = hashlib.file_digest(f, "sha256").hexdigest()
                if cached == entry["sha256"]:
                    record.event("cached", file=name, sha256=cached)
                    print(f"{name}: verified locally", flush=True)
                    continue
            print(f"Downloading {name} ({entry['size']:,} bytes)", flush=True)
            with tempfile.TemporaryDirectory(dir=source) as tmp:
                partial = Path(tmp) / name
                digest = hashlib.sha256()
                with requests.get(f"{base}/{entry['path']}", stream=True, timeout=(15, 180)) as response:
                    response.raise_for_status()
                    with partial.open("wb") as out:
                        for chunk in response.iter_content(4 * 1024 * 1024):
                            out.write(chunk)
                            digest.update(chunk)
                if partial.stat().st_size != entry["size"] or digest.hexdigest() != entry["sha256"]:
                    raise ValueError(f"Size or SHA-256 mismatch for {name}")
                partial.replace(path)
            record.event("downloaded", file=name, sha256=entry["sha256"])


def run(script, *args):
    subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("all", *STEPS), default="all", nargs="?")
    parser.add_argument("--source", type=Path, default=ROOT / "data", help="Local Parquet directory")
    args = parser.parse_args()
    source = args.source.resolve()
    manifest = json.loads((ROOT / "source.json").read_text())
    steps = STEPS if args.step == "all" else (args.step,)
    if args.step != "download":
        required = ["VK_DORIS_HOST", "VK_DORIS_PORT", "VK_DORIS_USER"]
        if "load" in steps:
            required.append("VK_DORIS_BE_URL")
        missing = [key for key in required if not os.environ.get(key)]
        if "VK_DORIS_PASSWORD" not in os.environ:
            missing.append("VK_DORIS_PASSWORD")
        if missing:
            parser.error("Set the variables in warehouse/.env first: " + ", ".join(missing))
    for step in steps:
        print(f"== {step} ==", flush=True)
        if step == "download":
            download(source, manifest)
        elif step == "schema":
            run("apply_sql.py", "--bootstrap", ROOT / "create-database.sql")
            run("apply_sql.py", ROOT / "schema.sql")
        elif step == "load":
            for name in manifest["files"]:
                run("load_parquet.py", source, name)
        elif step == "etl":
            run("build.py")
        else:
            run("verify.py", source)


if __name__ == "__main__":
    main()
