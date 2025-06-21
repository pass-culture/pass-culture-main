"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/tcoudray-pass/PC-36367-script-to-fill-dates/api/src/pcapi/scripts/fill_finalization_date/main.py

"""

import argparse
import datetime
import logging
import statistics
import time

import psycopg2.errors
import pytz
import sqlalchemy as sa

from pcapi.models import db


logger = logging.getLogger(__name__)


REPORT_EVERY = 100_000
AUTOVACUUM_THRESHOLD = 0.22


def _get_eta(end: int, current: int, elapsed_per_batch: list[int], batch_size: int) -> str:
    left_to_do = end - current
    seconds_eta = left_to_do / batch_size * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    str_eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return str_eta


def _get_max_id() -> int:
    result = db.session.execute(sa.text("SELECT MAX(id) FROM offer")).fetchone()
    return result[0] if result and result[0] is not None else 0


def _get_dead_tuple_ratio(max_id: int) -> float:
    # Important to not use sqlalchemy cache
    db.session.rollback()
    result = db.session.execute(
        sa.text(
            """
                SELECT n_dead_tup::float / NULLIF(:max_id, 0) AS dead_tuple_ratio
                FROM pg_stat_user_tables
                WHERE relname = 'offer';
            """
        ),
        {"max_id": max_id},
    ).fetchone()

    return result[0] if result else 0.0


def _wait_for_autovacuum(max_id: int) -> None:
    while True:
        ratio = _get_dead_tuple_ratio(max_id)

        if ratio < AUTOVACUUM_THRESHOLD:
            logger.info("Dead tuple ratio is back to %.2f%%, resuming...", ratio * 100)
            break
        logger.info("Dead tuple ratio is %.2f%%, sleeping for 60 seconds...", ratio * 100)
        time.sleep(600)


FINALIZATION_DATETIME_UPDATE_QUERY = """
UPDATE offer
SET "finalizationDatetime" = '1970-01-01 00:00:00'::timestamp
WHERE id BETWEEN :start AND :end
    AND "validation" != 'DRAFT'
    AND "finalizationDatetime" is NULL;
"""

PUBLICATION_DATETIME_UPDATE_QUERY = """
UPDATE offer
SET
    "publicationDatetime" = '1970-01-01 00:00:00'::timestamp
WHERE id BETWEEN :start AND :end
    AND "isActive" is TRUE
    AND "publicationDatetime" is NULL;
"""


def execute_query(query: str, i: int, batch_size: int) -> None:
    nb_retry = 3
    while nb_retry > 0:
        try:
            db.session.execute(sa.text(query), params={"start": i, "end": i + batch_size})
            return
        except psycopg2.errors.OperationalError as e:
            logger.info("Erreur de type %s sur les lignes entre %s et %s", type(e).__name__, i, i + batch_size)
            db.session.rollback()
            nb_retry -= 1
            if nb_retry == 0:
                raise


def fill_offer_lifecycle_datetime(
    update_query: str,
    starting_id: int,
    ending_id: int,
    batch_size: int,
    not_dry: bool = False,
    wait_autovacuum: bool = False,
) -> None:
    db.session.execute(sa.text("SET SESSION statement_timeout = '300s'"))
    max_id = _get_max_id()
    logger.info("Max ID for the 'offer' table: %d", max_id)

    elapsed_per_batch = []
    to_report = 0
    for i in range(starting_id, ending_id, batch_size + 1):
        start_time = time.perf_counter()

        execute_query(update_query, i, batch_size)

        if not_dry:
            db.session.commit()
        else:
            db.session.rollback()

        if wait_autovacuum:
            ratio = _get_dead_tuple_ratio(max_id)
            if ratio >= AUTOVACUUM_THRESHOLD:
                logger.info("Dead tuple ratio %.2f%% exceeds threshold (20%%). Pausing execution...", ratio * 100)
                _wait_for_autovacuum(max_id)

        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(ending_id, starting_id, elapsed_per_batch, batch_size)
        to_report += batch_size
        if to_report >= REPORT_EVERY:
            to_report = 0
            logger.info("BATCH : id from %s | eta = %s", i, eta)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Fill offer lifecycle datetimes")
    parser.add_argument("--datetime-to-fill", type=str, help="Either 'FINALIZATION_DATETIME' or 'PUBLICATION_DATETIME'")
    parser.add_argument("--starting-id", type=int, default=0, help="starting offer id")
    parser.add_argument("--ending-id", type=int, default=0, help="ending offer id")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    parser.add_argument(
        "--wait-autovacuum", action="store_true", help="Let database start autovacuum when threshold has been hit"
    )
    args = parser.parse_args()

    update_query = None

    if args.datetime_to_fill == "FINALIZATION_DATETIME":
        update_query = FINALIZATION_DATETIME_UPDATE_QUERY
    elif args.datetime_to_fill == "PUBLICATION_DATETIME":
        update_query = PUBLICATION_DATETIME_UPDATE_QUERY
    else:
        raise ValueError('"datetime-to-fill" must be either equal to FINALIZATION_DATETIME or PUBLICATION_DATETIME')

    if args.starting_id > args.ending_id:
        raise ValueError('"starting-id" must be less than "ending-id"')

    logger.info(
        "Starting %s script for ids between %s and %s",
        args.datetime_to_fill,
        str(args.starting_id),
        str(args.ending_id),
    )

    fill_offer_lifecycle_datetime(
        update_query, args.starting_id, args.ending_id, args.batch_size, args.not_dry, args.wait_autovacuum
    )

    logger.info(
        "Finished %s script for ids between %s and %s",
        args.datetime_to_fill,
        str(args.starting_id),
        str(args.ending_id),
    )
