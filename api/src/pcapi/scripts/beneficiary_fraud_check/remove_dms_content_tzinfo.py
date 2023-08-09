import datetime
from functools import wraps
import logging
import time

import pytz
from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified

from pcapi.connectors.dms.models import parse_dms_datetime
from pcapi.core.fraud import models as fraud_models
from pcapi.models import db
from pcapi.repository import repository


logging.basicConfig()
logger = logging.getLogger("my-logger")
logger.setLevel(logging.DEBUG)


def timed(f):  # type: ignore[no-untyped-def]
    """This decorator prints the execution time for the decorated function."""

    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        logger.debug("%s ran in %ss", f.__name__, round(end - start, 2))
        return result

    return wrapper


def clear_line(n: int = 1) -> None:
    LINE_UP = "\033[1A"
    LINE_CLEAR = "\x1b[2K"
    for _ in range(n):
        print(LINE_UP, end=LINE_CLEAR)


def display_progress(start_time: float, start: int, current: int, end: int) -> None:
    progression = (current - start) / (end - start)
    elapsed_time = time.time() - start_time
    duration = elapsed_time / progression
    timestamp_eta = start_time + duration
    datetime_eta = datetime.datetime.fromtimestamp(timestamp_eta).astimezone(pytz.timezone("Europe/Paris"))
    time_eta = datetime.datetime.strftime(datetime_eta, "%H:%M:%S")
    print(f"{current:6d} / {end} -> {progression * 100:3.2f}% in {elapsed_time:.2f}s")
    print(f"ETA {time_eta} Estimated duration {duration:.2f}s")
    clear_line()


@timed
def remove_dms_content_tzinfo(dry_run: bool = True, batch_size: int = 1000) -> None:
    query = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        fraud_models.BeneficiaryFraudCheck.resultContent.isnot(None),
    ).order_by(fraud_models.BeneficiaryFraudCheck.id)
    max_id = db.session.query(func.max(fraud_models.BeneficiaryFraudCheck.id)).scalar()
    print(f"{max_id} beneficiary fraud checks to update")

    min_id = 0
    start_index = min_id
    start_time = time.time()
    subquery = query
    while start_index < max_id:
        subquery = query.filter(fraud_models.BeneficiaryFraudCheck.id > start_index)
        bfcs: list[fraud_models.BeneficiaryFraudCheck] = subquery.limit(batch_size).all()
        for bfc in bfcs:
            if not bfc.resultContent or not bfc.resultContent.get("registration_datetime"):
                continue

            try:
                old = datetime.datetime.fromisoformat(bfc.resultContent["registration_datetime"])
            except TypeError as te:
                print(f"{bfc.id} {bfc.resultContent['registration_datetime']}:\n{te}")
                continue

            if not old.tzinfo:
                continue

            bfc.resultContent["registration_datetime"] = parse_dms_datetime(old)
            flag_modified(bfc, "resultContent")

        if dry_run:
            db.session.rollback()
        else:
            repository.save(*bfcs)

        start_index += batch_size
        display_progress(start_time, min_id, min(start_index, max_id), max_id)

    print("Done")
