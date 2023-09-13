"""
Generate dsToken for offerers without one on Batch.
"""
from itertools import islice
from typing import Generator

from pcapi.core.offerers.api import generate_offerer_ds_token
from pcapi.core.offerers.models import Offerer
from pcapi.models import db


def get_offerers_without_dms_token(batch_size: int) -> Generator[Offerer, None, None]:
    """Fetch offerers from database, without loading all of them at once."""
    try:
        for offerer in Offerer.query.filter(Offerer.dsToken.is_(None)).yield_per(batch_size):
            yield offerer
    except Exception as err:
        print(f"Offerers fetch failed: {err}")
        raise
    print("All offerers fetched")


def get_offerers_chunks(chunk_size: int) -> Generator[list[Offerer], None, None]:
    offerers = get_offerers_without_dms_token(chunk_size)
    while True:
        chunk = list(islice(offerers, chunk_size))
        if chunk:
            yield chunk

        if len(chunk) < chunk_size:
            break


def run(dry_run: bool = True, chunk_size: int = 1000) -> None:
    message = "offerer without dms migration"
    print(f"Starting {message} ...")
    for chunk in get_offerers_chunks(chunk_size):
        for offerer in chunk:
            offerer.dsToken = generate_offerer_ds_token()
        print(f"Updated offerers {[offerer.id for offerer in chunk]}")
    if dry_run:
        db.session.rollback()
        print("Did rollback. Use dry_run = False if you want the script to commit.")
    else:
        db.session.commit()
        print("Did commit changes.")

    print(f"... {message} finished")
