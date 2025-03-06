import argparse
from datetime import datetime
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.finance.enum import DepositType
from pcapi.core.finance.models import Deposit
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

deposit_ids = [
    8077,
    10442,
    15947,
    16652,
    21131,
    22680,
    23018,
    23841,
    19515,
    4162298,
    136264,
    280317,
]


def update_deposits_expiration_dates(start_id: int = 0, bach_size: int = 1000) -> None:
    query = (
        Deposit.query.filter(
            Deposit.type.in_([DepositType.GRANT_15_17, DepositType.GRANT_18]),
            Deposit.expirationDate > datetime.utcnow(),
            Deposit.id.in_(deposit_ids),
        )
        .options(sa.orm.selectinload(Deposit.user))
        .order_by(Deposit.id.desc())
    )
    max_id = query.first().id

    while start_id <= max_id:
        deposits = query.filter(Deposit.id >= start_id, Deposit.id < start_id + bach_size).all()
        for deposit in deposits:
            # if deposit.user.age not in [15, 16, 17, 18, 19, 20, 21]:
            deposit.expirationDate = datetime.utcnow()
            logger.info(
                "Expired deposit %s because user %s is not in the right age range (%s)",
                deposit.id,
                deposit.user.id,
                deposit.user.age,
            )
            action_log = ActionHistory(
                actionType=ActionType.FRAUD_INFO_MODIFIED,
                user=deposit.user,
                authorUserId=1633706,  # yep, this is me
                comment="PC-34961: Rattrapage de deposit étendus par erreur, les dates de naissance des utilisateurs sont incorrectes",
            )
            db.session.add(action_log)

        start_id += bach_size
    logger.info("Done")


if __name__ == "__main__":
    # https://github.com/pass-culture/pass-culture-main/blob/pc-34961/api/src/pcapi/scripts/correct_deposits_exp_date/main.py
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    update_deposits_expiration_dates()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
