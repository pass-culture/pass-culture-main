import argparse
import datetime
import logging
import random
import string
import time

import psycopg2.errors
import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


app.app_context().push()
logger = logging.getLogger(__name__)


def update_offer_batch(min_id: int, max_id: int) -> None:
    nb_retry = 3
    while nb_retry > 0:
        try:
            db.session.execute(
                sa.text(
                    """
                UPDATE offer SET "offererAddressId" = p."offererAddressId" from (
                select venue."offererAddressId", offer.id from offer join venue on offer."venueId" = venue.id where offer."offererAddressId" is null 
                and  (offer.url = '' or offer.url is NULL) 
                and offer.id >= :min_id 
                and offer.id <:max_id 
                ) as p 
                where offer.id = p.id
                and offer.id >= :min_id 
                and offer.id <:max_id ;            
                """
                ),
                {"min_id": min_id, "max_id": max_id},
            )
            return
        except Exception as e:
            logger.info(
                "Erreur de type %s sur les lignes offererAddressId entre %s et %s", type(e).__name__, min_id, max_id
            )
            db.session.rollback()
            nb_retry -= 1
            if nb_retry == 0:
                raise


def do_all_in_sql(min_id: int, max_id: int, batch_size: int, dry_run: bool, do_vacuum: bool = False) -> None:
    unique_name = "".join(random.choices(string.ascii_letters, k=5))
    start_time = datetime.datetime.utcnow()
    try:
        logger.info("starting script id %s at %s", unique_name, datetime.datetime.utcnow())
        db.session.execute(sa.text("SET SESSION statement_timeout = '400s'"))

        for i in range(min_id, max_id, batch_size):
            update_offer_batch(i, i + batch_size)
            logger.info("Updated offererAddressId rows between %s and %s ", i, i + batch_size)
            if not dry_run:
                db.session.commit()
            else:
                db.session.rollback()
    finally:
        db.session.execute(sa.text(f"SET SESSION statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}"))

    if not dry_run and do_vacuum:
        start = time.time()
        db.session.execute(sa.text("COMMIT;"))
        db.session.execute(sa.text("VACUUM ANALYZE offer;"))
        logger.info("VACUUM ANALYZE offer took %s seconds", time.time() - start)
    logger.info(
        "ending script id %s at %s and took %s",
        unique_name,
        datetime.datetime.utcnow(),
        datetime.datetime.utcnow() - start_time,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill offer address")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--min-id", type=int, default=0)
    parser.add_argument("--max-id", type=int, default=0)  # to be replaced by the actual max id
    parser.add_argument("--do-vacuum", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()
    try:
        if args.max_id <= args.min_id:
            raise ValueError("max_id must be greater than min_id")
        do_all_in_sql(args.min_id, args.max_id, args.batch_size, args.dry_run)
    except:
        db.session.rollback()
        raise
    if args.dry_run:
        db.session.rollback()
