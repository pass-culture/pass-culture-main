import argparse
import datetime
import logging
import statistics
import time

import pytz
import sqlalchemy as sa

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


def show_timeouts() -> None:
    statement_timeout = db.session.execute("SHOW statement_timeout").scalar()
    lock_timeout = db.session.execute("SHOW lock_timeout").scalar()

    logger.info("Current statement_timeout: %s", statement_timeout)
    logger.info("Current lock_timeout: %s", lock_timeout)


def delete_description(starting_id: int, ending_id: int, batch_size: int, not_dry: bool = False) -> None:
    db.session.execute(sa.text("SET SESSION statement_timeout = '400s'"))
    show_timeouts()
    elapsed_per_batch = []
    to_report = 0
    for i in range(starting_id, ending_id, batch_size):
        start_time = time.perf_counter()
        db.session.execute(
            """
            update offer set "description" = null
            where id between :start and :end and "productId" is not null
            """,
            params={"start": i, "end": i + batch_size},
        )
        if not_dry:
            db.session.commit()
        else:
            db.session.rollback()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(ending_id, starting_id, elapsed_per_batch, batch_size)
        to_report += batch_size
        if to_report >= REPORT_EVERY:
            to_report = 0
            logger.info("BATCH : id from %s | eta = %s", i, eta)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Delete description for offers linked to a product")
    parser.add_argument("--starting-id", type=int, default=0, help="starting offer id")
    parser.add_argument("--ending-id", type=int, default=0, help="ending offer id")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    if args.starting_id > args.ending_id:
        raise ValueError('"start" must be less than "end"')
    show_timeouts()
    delete_description(args.starting_id, args.ending_id, args.batch_size, args.not_dry)
