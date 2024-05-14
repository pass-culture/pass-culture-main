import argparse
import datetime
import logging
import statistics
import time

import pytz

from pcapi import settings
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


BATCH_SIZE = 10000

logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


def _get_eta(end_id: int, current: int, elapsed_per_batch: list) -> str:
    left_to_do = end_id - current
    eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


def _fill_products_cgu_compatibility_type(start_id: int, end_id: int) -> None:
    elapsed_per_batch = []
    logger.info("[fill_products_cgu_compatibility_type] BATCH_SIZE : %d", BATCH_SIZE)
    db.session.execute(
        """
        SET SESSION statement_timeout = '400s'
        """
    )
    for i in range(start_id, end_id, BATCH_SIZE):
        start_time = time.perf_counter()
        db.session.execute(
            """
            UPDATE "product"
            SET "gcuCompatibilityType" = 'PROVIDER_INCOMPATIBLE'
            WHERE product.id between :start and :end
            AND "isGcuCompatible"=false;          
            """,
            params={"start": i, "end": i + BATCH_SIZE},
        )
        db.session.commit()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(end_id, start_id, elapsed_per_batch)

        logger.info("[fill_products_cgu_compatibility_type] BATCH : id from %d | eta = %s", i, eta)
    db.session.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    args = parser.parse_args()
    logger.info("[fill_products_cgu_compatibility_type] start between %d and %d", args.start, args.end)
    if args.start > args.end:
        raise ValueError('"start" must be less than "end"')

    with app.app_context():
        _fill_products_cgu_compatibility_type(args.start, args.end)


if __name__ == "__main__":
    main()
