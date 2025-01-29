import argparse
import datetime
import logging
import random
import string
from typing import Any

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db


app.app_context().push()
logger = logging.getLogger(__name__)

DESCRIPTION = "Relocate Offers to OffererAddress after Venue's OffererAddress fix"
DEFAULT_BATCH_SIZE = 1000
DEFAULT_RETRIES = 3
DEFAULT_TIMEOUT = "400s"
DEFAULT_MIN_ID = 0
DEFAULT_MAX_ID = 1000000000
VENUE_ID = 17440
OA_ID = 17626
INCORRECT_OA_IDS = [94975, 96053]


def update_items(batch_size: int, retries: int, min_id: int, max_id: int) -> None:

    correct_oa = offerers_models.OffererAddress.query.filter(offerers_models.OffererAddress.id == OA_ID).one_or_none()
    if correct_oa is None:
        logger.info("IGNORED: OA #%s not found for Venue #%s", OA_ID, VENUE_ID)
        return

    for incorrect_oa_id in INCORRECT_OA_IDS:
        try:
            conditions = []
            conditions.append(offers_models.Offer.venueId == VENUE_ID)
            conditions.append(offers_models.Offer.offererAddressId == incorrect_oa_id)
            if min_id != DEFAULT_MIN_ID:
                conditions.append(offers_models.Offer.id >= min_id)
            if max_id != DEFAULT_MAX_ID:
                conditions.append(offers_models.Offer.id <= max_id)

            statement = sa.select(offers_models.Offer.id).where(sa.and_(*conditions))
            result = db.session.execute(statement=statement, execution_options={"yield_per": batch_size})
            for partition in result.partitions():
                ids = [id for id, in partition]
                left_retries = retries

                while left_retries > 0:
                    try:
                        offers_models.Offer.query.filter(offers_models.Offer.id.in_(ids)).update(
                            {offers_models.Offer.offererAddressId: OA_ID}, synchronize_session=False
                        )

                        logger.info(
                            "CORRECTED: updated offers [#%s -> #%s] from OA #%s to OA #%s for Venue #%s",
                            ids[0],
                            ids[-1],
                            incorrect_oa_id,
                            OA_ID,
                            VENUE_ID,
                        )
                        left_retries = 0
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        logger.info(
                            "ERROR: error updating offers [#%s -> #%s] from OA #%s to OA #%s for Venue #%s - %s",
                            ids[0],
                            ids[-1],
                            incorrect_oa_id,
                            OA_ID,
                            VENUE_ID,
                            type(e).__name__,
                        )
                        left_retries -= 1
                        if left_retries == 0:
                            raise

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.info(
                "NOT CORRECTED: offers not udpated from OA #%s to OA #%s for Venue #%s - %s",
                incorrect_oa_id,
                OA_ID,
                VENUE_ID,
                str(e),
            )
            continue


def apply_batch_script(parameters: Any) -> None:
    run_id = "".join(random.choices(string.ascii_letters, k=5))
    start_time = datetime.datetime.utcnow()
    logger.info("Starting script run #%s at %s", run_id, start_time)
    try:
        db.session.execute(
            sa.text("SET SESSION statement_timeout = :timeout"),
            {"timeout": parameters.timeout},
        )

        update_items(parameters.batch_size, parameters.retries, parameters.min_id, parameters.max_id)

    finally:
        db.session.execute(
            sa.text("SET SESSION statement_timeout = :timeout"),
            {"timeout": settings.DATABASE_STATEMENT_TIMEOUT},
        )

    if not parameters.dry_run:
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
    parser.add_argument("--min-id", type=int, default=DEFAULT_MIN_ID)
    parser.add_argument("--max-id", type=int, default=DEFAULT_MAX_ID)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    parser.add_argument("--timeout", type=str, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    if args.min_id < 0:
        raise ValueError("min_id argument should be a positive integer")
    if args.max_id < args.min_id:
        raise ValueError("max_id argument should be an integer greater than min_id")

    try:
        apply_batch_script(args)
    except:
        db.session.rollback()
        raise
    if args.dry_run:
        db.session.rollback()
