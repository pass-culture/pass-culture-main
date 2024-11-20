import argparse
import datetime
import logging
import statistics
import time

import psycopg2.errors
import pytz
from sqlalchemy import func
from sqlalchemy import text

from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


REPORT_EVERY = 100_000


def _get_eta(end: int, current: int, elapsed_per_batch: list[int], batch_size: int) -> str:
    left_to_do = end - current
    seconds_eta = left_to_do / batch_size * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    str_eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return str_eta


def execute_query(i: int, batch_size: int) -> None:
    nb_retry = 3
    while nb_retry > 0:
        try:
            db.session.execute(
                text(
                    """
                    UPDATE product_mediation
                    SET uuid = RIGHT(url, 36) where id between :start and :end;
                """
                ),
                params={"start": i, "end": i + batch_size},
            )
            return
        except psycopg2.errors.OperationalError as e:
            logger.info("Erreur de type %s sur les lignes entre %s et %s", type(e).__name__, i, i + batch_size)
            db.session.rollback()
            nb_retry -= 1
            if nb_retry == 0:
                raise


def duplicate_uuid(batch_size: int, not_dry: bool = False) -> None:
    max_id = db.session.query(func.max(offers_models.ProductMediation.id)).scalar()
    if not max_id:
        logger.info("No data to process")
        return
    elapsed_per_batch = []
    to_report = 0
    for i in range(1, max_id, batch_size + 1):
        start_time = time.perf_counter()

        execute_query(i, batch_size)

        if not_dry:
            db.session.commit()
        else:
            db.session.rollback()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(max_id, 1, elapsed_per_batch, batch_size)
        to_report += batch_size
        if to_report >= REPORT_EVERY:
            to_report = 0
            logger.info("BATCH : id from %s | eta = %s", i, eta)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Duplicate production mediation uuid to new column")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    duplicate_uuid(args.batch_size, args.not_dry)
