import argparse
import datetime
import logging
import statistics
import time

import pytz

from pcapi.models import db


logger = logging.getLogger(__name__)

BATCH_SIZE = 1_000
REPORT_EVERY = 100_000


def _get_eta(end: int, current: int, elapsed_per_batch: list[int]) -> str:
    left_to_do = end - current
    seconds_eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    str_eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return str_eta


def delete_description(starting_id: int, ending_id: int, not_dry: bool = False) -> None:
    elapsed_per_batch = []
    to_report = 0
    for i in range(starting_id, ending_id, BATCH_SIZE):
        start_time = time.perf_counter()
        db.session.execute(
            """
            update offer set "description" = null
            where id between :start and :end and "productId" is not null
            """,
            params={"start": i, "end": i + BATCH_SIZE},
        )
        if not_dry:
            db.session.commit()
        else:
            db.session.rollback()
        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(ending_id, starting_id, elapsed_per_batch)
        to_report += BATCH_SIZE
        if to_report >= REPORT_EVERY:
            to_report = 0
            logger.info("BATCH : id from %s | eta = %s", i, eta)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Delete description for offers linked to a product")
    parser.add_argument("--starting-id", type=int, default=0, help="starting offer id")
    parser.add_argument("--ending-id", type=int, default=0, help="ending offer id")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    if args.starting_id > args.ending_id:
        raise ValueError('"start" must be less than "end"')

    delete_description(args.starting_id, args.ending_id, args.not_dry)
