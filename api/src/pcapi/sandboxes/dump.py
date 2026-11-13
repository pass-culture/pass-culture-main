"""Write and restore the tracked data dump of the industrial sandbox with the `pg_dump` and `pg_restore` of the local
PostgreSQL container, run through `docker exec`, so that their version is always the server's.

The dump is not checked against the sandbox code: it is regenerated and committed manually (to refresh its dates, or after
changes to the sandbox data).
"""

import pathlib
import shutil
import subprocess
import typing
import urllib.parse


SANDBOXES_DIRECTORY = pathlib.Path(__file__).resolve().parent
DUMP_PATH = SANDBOXES_DIRECTORY / "industrial.dump"
# Tables of the `public` schema whose data is not dumped
# (keep in sync with the `TRUNCATE` of `save_sandbox.restore_industrial_sandbox`)
EXCLUDED_TABLES = ("alembic_version", "spatial_ref_sys")


class DumpError(Exception):
    pass


def write_dump(container: str, database_url: str) -> None:
    """Dump the data of the `public` schema, excluding migrations state and the PostGIS reference data."""
    dump_content = _run_in_container(
        container,
        [
            "pg_dump",
            "--data-only",
            "--format=custom",
            "--schema=public",
            *(f"--exclude-table-data=public.{table}" for table in EXCLUDED_TABLES),
            *_get_connection_arguments(database_url),
        ],
    )
    DUMP_PATH.write_bytes(dump_content)


def check_restorable(container: str) -> None:
    """Raise `DumpError` if the dump cannot be restored, before the tables are emptied."""
    if not DUMP_PATH.is_file():
        raise DumpError(f"no dump in {SANDBOXES_DIRECTORY}")
    _run_in_container(container, ["pg_restore", "--version"])


def restore_dump(container: str, database_url: str) -> None:
    """Restore the data of the dump (in tables that are expected to be emptied beforehand)."""
    with open(DUMP_PATH, "rb") as dump_file:
        _run_in_container(
            container,
            [
                "pg_restore",
                "--data-only",
                "--disable-triggers",
                "--single-transaction",
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                *_get_connection_arguments(database_url),
            ],
            stdin=dump_file,
        )


def _get_connection_arguments(database_url: str) -> tuple[str, str]:
    url = urllib.parse.urlsplit(database_url)
    return f"--username={url.username}", f"--dbname={url.path.lstrip('/')}"


def _run_in_container(container: str, command: list[str], stdin: typing.IO[bytes] | None = None) -> bytes:
    if shutil.which("docker") is None:
        raise DumpError("`docker` is not on PATH")
    result = subprocess.run(
        ["docker", "exec", "-i", container, *command], stdin=stdin, capture_output=True, check=False
    )
    if result.returncode != 0:
        lines = result.stderr.decode(errors="replace").strip().splitlines() or [f"exit code {result.returncode}"]
        raise DumpError(next((line for line in lines if "error" in line.lower()), lines[-1]))
    return result.stdout
