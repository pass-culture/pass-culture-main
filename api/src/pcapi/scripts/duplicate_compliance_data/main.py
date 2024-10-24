import argparse
import datetime
import logging
import statistics
import time

import psycopg2.errors
import pytz

from pcapi.models import db


MIN_OFFER_WITH_COMPLIANCE_SCORE = 76_375_500  # 76_375_533 is the first offer with a compliance score

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
                """
                    insert into offer_compliance ("offerId", compliance_score, compliance_reasons)
                        select id,
                            ("jsonData"->>'complianceScore')::smallint as compliance_score,
                            array(select jsonb_array_elements_text("jsonData"->'complianceReasons')) as compliance_reasons
                        from offer
                        where id between :start and :end and ("jsonData"->>'complianceScore' is not null)
                        on conflict ("offerId") do nothing;
                """,
                params={"start": i, "end": i + batch_size},
            )
            return
        except psycopg2.errors.OperationalError as e:
            logger.info("Erreur de type %s sur les lignes entre %s et %s", type(e).__name__, i, i + batch_size)
            db.session.rollback()
            nb_retry -= 1
            if nb_retry == 0:
                raise


def duplicate_compliance_score(starting_id: int, ending_id: int, batch_size: int, not_dry: bool = False) -> None:
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

    parser = argparse.ArgumentParser(description="Duplicate offer compliance score to offer_compliance table")
    parser.add_argument("--starting-id", type=int, default=0, help="starting offer id")
    parser.add_argument("--ending-id", type=int, default=0, help="ending offer id")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    if args.starting_id > args.ending_id:
        raise ValueError('"start" must be less than "end"')
    if args.starting_id < MIN_OFFER_WITH_COMPLIANCE_SCORE:
        raise ValueError('"start" must be greater than 76_375_499')

    duplicate_compliance_score(args.starting_id, args.ending_id, args.batch_size, args.not_dry)
