import argparse
from contextlib import contextmanager
import logging
import time
import typing

from dateutil.relativedelta import relativedelta
import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.enum import DepositType
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

app.app_context().push()


@contextmanager
def time_print(task_name: str) -> typing.Generator:
    t = time.time()
    try:
        yield
    finally:
        logger.info("%s took %s seconds.", task_name, round(time.time() - t, 2))


def set_deposit_expiration_date_to_21st_birthday(deposit: finance_models.Deposit) -> None:
    user = deposit.user
    if len(user.deposits) == 1:
        deposit_to_extend = deposit

    if len(user.deposits) > 1:
        # find the correct deposit to extend
        # if not the current one, return
        deposit_types = [d.type for d in user.deposits]
        if DepositType.GRANT_18 in deposit_types:
            # if there is a GRANT_18 deposit, we want to extend the GRANT_18
            deposit_to_extend = next(d for d in user.deposits if d.type == DepositType.GRANT_18)
            if deposit_to_extend.id != deposit.id:
                # this is not the current deposit, it will be processed by another iteration
                return
        elif DepositType.GRANT_17_18 in deposit_types:
            # GRANT_17_18 needs no extension, they are up to date
            return

        elif DepositType.GRANT_15_17 in deposit_types:
            # If no GRANT_18 deposit, we want to extend the GRANT_15_17
            deposit_to_extend = next(d for d in user.deposits if d.type == DepositType.GRANT_15_17)
            if deposit_to_extend.id != deposit.id:
                # this is not the current deposit, it will be processed by another iteration
                return
        else:
            # Should not happen, but you know, better safe than sorry
            logger.error("Impossible state with user %s deposits. No known deposit type %s", user.id, deposit_types)
            return

    if not user.birth_date:
        logger.error("Impossible state with user %s birth date. No birth date", user.id)
        return
    twenty_first_birthday = user.birth_date + relativedelta(years=21)
    deposit_to_extend.expirationDate = twenty_first_birthday


def run(batch_size: int, start_from_id: int) -> None:
    deposit_query = (
        finance_models.Deposit.query.filter(
            finance_models.Deposit.type.in_(
                [finance_models.DepositType.GRANT_18, finance_models.DepositType.GRANT_15_17]
            ),
            finance_models.Deposit.id >= start_from_id,
        )
        .options(sa.orm.selectinload(finance_models.Deposit.user))
        .order_by(finance_models.Deposit.id)
    )

    with time_print("Counting deposits to update"):
        deposit_count = (
            deposit_query.count()
        )  # this is slow-ish. Acceptable for a one-time script (less than 30 seconds in staging env)
        logger.info("Found %s deposits", deposit_count)

    page = 1
    latest_deposit_id = start_from_id - 1
    has_next_page = True
    while has_next_page:
        deposits = deposit_query.filter(finance_models.Deposit.id > latest_deposit_id).limit(batch_size).all()
        logger.info("Processing page %s of %s", page, deposit_count // batch_size)
        page += 1
        with transaction():
            for deposit in deposits:
                latest_deposit_id = deposit.id
                set_deposit_expiration_date_to_21st_birthday(deposit)
        logger.info("Latest deposit id processed: %s", latest_deposit_id)
        has_next_page = bool(deposits)


if __name__ == "__main__":
    # https://github.com/pass-culture/pass-culture-main/blob/pc-34432/api/src/pcapi/scripts/update_deposit_expiration_dates/main.py

    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int)
    parser.add_argument("--from_id", type=int)
    args = parser.parse_args()

    batch = args.batch_size or 100
    from_id = args.from_id or 0
    with time_print("Running script"):
        run(batch_size=batch, start_from_id=from_id)

    logger.info("Done")
