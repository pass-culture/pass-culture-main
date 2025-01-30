import argparse
import datetime
import logging
import random
import string

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


app.app_context().push()
logger = logging.getLogger(__name__)

DESCRIPTION = "Delete incorrect OffererAddresses after OffererAddress fix for Venues and Offers"
DEFAULT_BATCH_SIZE = 1000
DEFAULT_RETRIES = 3
DEFAULT_TIMEOUT = "400s"


def delete_items(batch_size: int, retries: int, incorrect_oa_ids: list[int]) -> None:
    try:
        for partition in [incorrect_oa_ids[i : i + batch_size] for i in range(0, len(incorrect_oa_ids), batch_size)]:
            left_retries = retries
            while left_retries > 0:
                try:
                    offerers_models.OffererAddress.query.filter(
                        offerers_models.OffererAddress.id.in_(partition),
                    ).delete()

                    logger.info(
                        "CORRECTED: deleted OAs [#%s -> #%s]",
                        partition[0],
                        partition[-1],
                    )
                    left_retries = 0
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.info(
                        "ERROR: error deleting OAs [#%s -> #%s] - %s",
                        partition[0],
                        partition[-1],
                        type(e).__name__,
                    )
                    db.session.rollback()
                    left_retries -= 1
                    if left_retries == 0:
                        raise

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.info(
            "NOT CORRECTED: OAs not deleted - %s",
            str(e),
        )


def apply_batch_script(batch_size: int, retries: int, timeout: str, dry_run: bool, incorrect_oa_ids: list[int]) -> None:
    run_id = "".join(random.choices(string.ascii_letters, k=5))
    start_time = datetime.datetime.utcnow()
    logger.info("Starting script run #%s at %s", run_id, start_time)
    try:
        db.session.execute(
            sa.text("SET SESSION statement_timeout = :timeout"),
            {"timeout": timeout},
        )

        delete_items(batch_size, retries, incorrect_oa_ids)

    finally:
        db.session.execute(
            sa.text("SET SESSION statement_timeout = :timeout"),
            {"timeout": settings.DATABASE_STATEMENT_TIMEOUT},
        )

    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()

    end_time = datetime.datetime.utcnow()
    logger.info(
        "Ending script run #%s at %s. Total run time: %s",
        run_id,
        end_time,
        end_time - start_time,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    parser.add_argument("--timeout", type=str, default=DEFAULT_TIMEOUT)
    parser.add_argument("--incorrect-oa-ids", nargs="+", type=int, required=True)
    args = parser.parse_args()

    try:
        apply_batch_script(args.batch_size, args.retries, args.timeout, args.dry_run, args.incorrect_oa_ids)
    except:
        db.session.rollback()
        raise
    if args.dry_run:
        db.session.rollback()
