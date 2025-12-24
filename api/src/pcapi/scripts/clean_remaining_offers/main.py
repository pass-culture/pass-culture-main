import argparse
import csv
import logging
import os
import typing

import sqlalchemy as sa

from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


app.app_context().push()

BATCH_SIZE = 100


def get_offer_ids() -> typing.Iterator[int]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f"{namespace_dir}/offer_ids.csv", "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield int(row["id"])


def fix_offers(dry_run: bool = True, batch_size: int = BATCH_SIZE) -> None:
    buffer = []
    offer_fixed = 0
    for id in get_offer_ids():
        logger.info("offer_id : %s", id)
        offer_fixed += 1
        buffer.append(int(id))
        if len(buffer) >= batch_size:
            _update_batch(buffer, dry_run)
            buffer.clear()

    if buffer:
        _update_batch(buffer, dry_run)
    logger.info("Offers updated : %s", offer_fixed)


def _update_batch(offer_ids: list[int], dry_run: bool) -> None:
    try:
        db.session.execute(
            sa.text("""
                UPDATE offer
                SET "jsonData" = '{}'::jsonb,
                    "durationMinutes" = NULL,
                    "description" = NULL
                WHERE id in :offer_ids;
            """),
            params={"offer_ids": tuple(offer_ids)},
        )
    except:
        db.session.rollback()
        raise
    else:
        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="mais qui va lire ça ?")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    dry_run = args.dry_run
    fix_offers(dry_run)
