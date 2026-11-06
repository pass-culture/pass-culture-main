"""Write and restore the tracked data dump of the industrial sandbox with the `pg_dump` and `pg_restore` of the local
PostgreSQL container, run through `docker exec`, so that their version is always the server's.

The dump is only restored when the hash stored next to it is the hash of the current sandbox code. This module only
depends on the standard library, so that the CI checks that hash without the application:

    python3 -I src/pcapi/sandboxes/dump.py
"""

import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import typing
import urllib.parse


SANDBOXES_DIRECTORY = pathlib.Path(__file__).resolve().parent
DUMP_PATH = SANDBOXES_DIRECTORY / "industrial.dump"
HASH_PATH = SANDBOXES_DIRECTORY / "industrial.dump.sha256"
EXCLUDED_PATHS = ("industrial.dump", "industrial.dump.sha256", "thumbs/mediations/")


class DumpError(Exception):
    pass


def compute_hash(directory: pathlib.Path = SANDBOXES_DIRECTORY) -> str:
    """Return the sha256 of the files of `directory`, except the dump, its hash and the generated files."""
    digest = hashlib.sha256()
    relative_paths = sorted(
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    for relative_path in relative_paths:
        if not relative_path.startswith(EXCLUDED_PATHS):
            digest.update(relative_path.encode() + b"\0")
            digest.update(hashlib.sha256((directory / relative_path).read_bytes()).digest())
    return digest.hexdigest()


def is_up_to_date() -> bool:
    """Return whether the dump was written from the current sandbox code."""
    return HASH_PATH.is_file() and HASH_PATH.read_text().strip() == compute_hash()


def write_dump(container: str, database_url: str) -> None:
    """Dump the data of the `public` schema, except the migrations state and the PostGIS reference data."""
    dump_content = _run_in_container(
        container,
        "pg_dump",
        "--data-only",
        "--format=custom",
        "--schema=public",
        "--exclude-table-data=public.alembic_version",
        "--exclude-table-data=public.spatial_ref_sys",
        *_get_connection_arguments(database_url),
    )
    DUMP_PATH.write_bytes(dump_content)
    HASH_PATH.write_text(f"{compute_hash()}\n")


def list_dumped_tables(container: str) -> list[str]:
    """Return the tables whose data is in the dump, after checking that the dump is up to date with the code."""
    if not DUMP_PATH.is_file():
        raise DumpError(f"no dump in {SANDBOXES_DIRECTORY}")
    if not is_up_to_date():
        raise DumpError("sandbox code changed since the dump, run with `--update-dump true` to refresh it")
    with open(DUMP_PATH, "rb") as dump_file:
        table_of_contents = _run_in_container(container, "pg_restore", "--list", stdin=dump_file)
    return re.findall(r"^\d+; \d+ \d+ TABLE DATA public (\S+) ", table_of_contents.decode(), re.MULTILINE)


def restore_dump(container: str, database_url: str) -> None:
    """Restore the data of the dump, in tables emptied beforehand."""
    with open(DUMP_PATH, "rb") as dump_file:
        _run_in_container(
            container,
            "pg_restore",
            "--data-only",
            "--disable-triggers",
            "--single-transaction",
            "--exit-on-error",
            "--no-owner",
            "--no-privileges",
            *_get_connection_arguments(database_url),
            stdin=dump_file,
        )


def _get_connection_arguments(database_url: str) -> tuple[str, str]:
    url = urllib.parse.urlsplit(database_url)
    return f"--username={url.username}", f"--dbname={url.path.lstrip('/')}"


def _run_in_container(container: str, *command: str, stdin: typing.IO[bytes] | None = None) -> bytes:
    if shutil.which("docker") is None:
        raise DumpError("`docker` is not on PATH")
    result = subprocess.run(
        ["docker", "exec", "-i", container, *command], stdin=stdin, capture_output=True, check=False
    )
    if result.returncode != 0:
        lines = result.stderr.decode(errors="replace").strip().splitlines() or [f"exit code {result.returncode}"]
        raise DumpError(next((line for line in lines if "error" in line.lower()), lines[-1]))
    return result.stdout


if __name__ == "__main__":
    if not is_up_to_date():
        sys.exit(
            "The industrial sandbox dump is outdated: run `flask sandbox -n industrial --update-dump true` from `api/`"
            " and commit `src/pcapi/sandboxes/industrial.dump` and its hash"
        )
