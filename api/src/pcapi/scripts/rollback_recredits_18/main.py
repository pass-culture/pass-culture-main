import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

app.app_context().push()

UNDERAGE_RECREDITS = [
    finance_models.RecreditType.RECREDIT_15,
    finance_models.RecreditType.RECREDIT_16,
    finance_models.RecreditType.RECREDIT_17,
]

user_ids = [
    3896748,
    4313309,
    4120174,
    3564133,
    3564133,
    2580681,
    2580681,
    4488799,
    3075449,
    4304607,
    4971261,
    3895298,
    3895298,
    4361374,
    2532254,
    2532254,
    4319284,
    2736502,
    2736502,
    3627975,
    3627975,
    2461327,
    2461327,
    2363368,
    2363368,
    3856651,
    4654304,
    3580077,
    3580077,
    2768193,
    2768193,
    4304077,
]


def rollback_recredit_underage_to_user_18(deposit: finance_models.Deposit) -> None:
    recredits = deposit.recredits
    if deposit.type != finance_models.DepositType.GRANT_18:
        logger.info(
            "Deposit %s is not a 18 grant, no need to rollback recredit underage to user 18",
            deposit.id,
        )
        return
    for recredit in recredits:
        if recredit.recreditType in UNDERAGE_RECREDITS:
            recredited_amount = recredit.amount
            deposit.amount -= recredited_amount
            db.session.delete(recredit)
            db.session.add(deposit)

            logger.info("Un-recredit %s from deposit %s", recredited_amount, deposit.id)


def run() -> None:
    deposit_query = finance_models.Deposit.query.filter(
        finance_models.Deposit.type == finance_models.DepositType.GRANT_18,
        finance_models.Deposit.userId.in_(user_ids),
        # sa.or_(
        #     finance_models.Deposit.recredits.any(recreditType=finance_models.RecreditType.RECREDIT_15),
        #     finance_models.Deposit.recredits.any(recreditType=finance_models.RecreditType.RECREDIT_16),
        #     finance_models.Deposit.recredits.any(recreditType=finance_models.RecreditType.RECREDIT_17),
        # ),
        # statement timeout in staging -> I use user ids instead
    )
    for deposit in deposit_query:
        with transaction():
            logger.info(
                "Rollback recredit underage for User %s (deposit %s %s)", deposit.user.id, deposit.id, deposit.type
            )
            rollback_recredit_underage_to_user_18(deposit)


if __name__ == "__main__":

    run()
    logger.info("Done")
