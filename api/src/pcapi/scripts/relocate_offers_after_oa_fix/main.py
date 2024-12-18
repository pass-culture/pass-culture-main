import argparse
import datetime
import logging
import random
import string

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
DATA_MODEL = ("venue_id", "correct_oa_id", "incorrect_oa_id")
DATA = [
    (9731, 98985, 95225),
    (9731, 98985, 95576),
    (121823, 27031, 95193),
    (13960, 27061, 89900),
    (40711, 21098, 95058),
    (5288, 55579, 89710),
    (57776, 46293, 95323),
]


def update_items(batch_size: int, retries: int) -> None:
    items_to_correct = [dict(zip(DATA_MODEL, item)) for item in DATA]
    for item in items_to_correct:
        venue_id = item.get("venue_id")
        correct_oa_id = item.get("correct_oa_id")
        incorrect_oa_id = item.get("incorrect_oa_id")
        try:
            correct_oa = offerers_models.OffererAddress.query.filter(
                offerers_models.OffererAddress.id == correct_oa_id
            ).one_or_none()
            if correct_oa is None:
                logger.info("IGNORED: OA #%s not found for Venue #%s", correct_oa_id, venue_id)
                continue

            statement = (
                sa.select(offers_models.Offer.id)
                .where(offers_models.Offer.venueId == venue_id)
                .where(offers_models.Offer.offererAddressId == incorrect_oa_id)
            )
            result = db.session.execute(statement=statement, execution_options={"yield_per": batch_size})
            for partition in result.partitions():
                ids = [id for id, in partition]
                left_retries = retries

                while left_retries > 0:
                    try:
                        offers_models.Offer.query.filter(offers_models.Offer.id.in_(ids)).update(
                            {offers_models.Offer.offererAddressId: correct_oa_id}, synchronize_session=False
                        )

                        logger.info(
                            "CORRECTED: updated offers [#%s -> #%s] from OA #%s to OA #%s for Venue #%s",
                            ids[0],
                            ids[-1],
                            incorrect_oa_id,
                            correct_oa_id,
                            venue_id,
                        )
                        left_retries = 0
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        logger.info(
                            "ERROR: error updating offers [#%s -> #%s] from OA #%s to OA #%s for Venue #%s - %s",
                            ids[0],
                            ids[-1],
                            incorrect_oa_id,
                            correct_oa_id,
                            venue_id,
                            type(e).__name__,
                        )
                        db.session.rollback()
                        left_retries -= 1
                        if left_retries == 0:
                            raise

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.info(
                "NOT CORRECTED: offers not udpated from OA #%s to OA #%s for Venue #%s - %s",
                incorrect_oa_id,
                correct_oa_id,
                venue_id,
                str(e),
            )
            continue


def apply_batch_script(batch_size: int, retries: int, timeout: str, dry_run: bool) -> None:
    run_id = "".join(random.choices(string.ascii_letters, k=5))
    start_time = datetime.datetime.utcnow()
    logger.info("Starting script run #%s at %s", run_id, start_time)
    try:
        db.session.execute(
            sa.text("SET SESSION statement_timeout = :timeout"),
            {"timeout": timeout},
        )

        update_items(batch_size, retries)

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
    args = parser.parse_args()

    try:
        apply_batch_script(args.batch_size, args.retries, args.timeout, args.dry_run)
    except:
        db.session.rollback()
        raise
    if args.dry_run:
        db.session.rollback()
