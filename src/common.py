"""Path, penyimpanan atomik, checksum, dan koneksi analitik."""

import hashlib
import json
import os
from pathlib import Path

import duckdb


def find_project_root(start=None):
    current = Path(start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "requirements.txt").is_file() and (
            candidate / "data" / "README.md"
        ).is_file():
            return candidate
    raise FileNotFoundError("Buka Jupyter dari akar repository atau folder notebooks/.")


def prepare_directories(root):
    for folder in ("data/raw", "data/processed", "output/figures"):
        (Path(root) / folder).mkdir(parents=True, exist_ok=True)


def sha256_file(path):
    checksum = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def read_json(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Belum ada {path.name}; jalankan notebook sebelumnya.")
    return json.loads(path.read_text(encoding="utf-8"))


def sink_parquet_atomic(frame, path):
    """Sink streaming; target lama dipertahankan jika penulisan gagal."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.parquet")
    try:
        frame.sink_parquet(temporary, compression="zstd", row_group_size=50_000)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def sql_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def connect_analytics(root):
    connection = duckdb.connect()
    temporary = Path(root) / "data" / "processed" / "_duckdb_tmp"
    temporary.mkdir(parents=True, exist_ok=True)
    connection.execute(
        f"SET memory_limit = {sql_literal(os.getenv('DUCKDB_MEMORY_LIMIT', '2GB'))}"
    )
    connection.execute(f"SET temp_directory = {sql_literal(temporary)}")
    connection.execute("SET threads = 4")
    return connection
