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


def _get_max_id() -> int:
    result = db.session.execute(sa.text("SELECT MAX(id) FROM offer")).fetchone()
    return result[0] if result and result[0] is not None else 0


def run_batch(start: int, end: int, attempt_size: int) -> int:
    nb_retry = 10
    while nb_retry > 0:
        try:
            db.session.execute(
                sa.text(
                    """
                        UPDATE offer
                        SET "jsonData" = '{}'::jsonb,
                            "durationMinutes" = NULL
                        WHERE "productId" is not null AND id BETWEEN :start AND :end;
                        """
                ),
                params={"start": start, "end": start + attempt_size},
            )
            return attempt_size
        except sa.exc.OperationalError as e:
            logger.info(
                "Erreur de type %s sur les lignes entre %s et %s (batch_size=%s)",
                type(e).__name__,
                start,
                start + attempt_size,
                attempt_size,
            )
            db.session.rollback()
            nb_retry -= 1

            if attempt_size > 1:
                attempt_size = max(1, attempt_size // 5)

            if nb_retry == 0:
                raise RuntimeError(f"Failuring start:{start} end:{end} batch_size:{attempt_size}") from e

    return attempt_size


def execute_query(i: int, batch_size: int) -> None:
    current = i
    end = current + batch_size

    while current < end:
        remaining = end - current
        attempt_size = min(batch_size, remaining)
        try:
            attempt_size = run_batch(current, current + attempt_size, attempt_size)
        except RuntimeError as e:
            logger.error("Fatal error during sub-batch : %s", e)
            raise
        current += attempt_size


def remove_offer_extraData_if_offer_linked_to_product(
    starting_id: int, ending_id: int, batch_size: int, timeout: int, not_dry: bool = False
) -> None:
    db.session.execute(sa.text(f"SET SESSION statement_timeout = '{timeout}s'"))
    max_id = _get_max_id()
    logger.info("Max ID for the 'offer' table: %d", max_id)

    elapsed_per_batch = []
    to_report = 0
    for i in range(starting_id, ending_id, batch_size + 1):
        start_time = time.perf_counter()

        execute_query(i, batch_size)

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

    parser = argparse.ArgumentParser(
        description="Remove useless key from offer jsonData if offer is linked to a product"
    )
    parser.add_argument("--starting-id", type=int, default=0, help="starting offer id")
    parser.add_argument("--ending-id", type=int, default=0, help="ending offer id")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    if args.starting_id > args.ending_id:
        raise ValueError('"start" must be less than "end"')

    remove_offer_extraData_if_offer_linked_to_product(
        args.starting_id,
        args.ending_id,
        args.batch_size,
        args.timeout,
        args.not_dry,
    )
