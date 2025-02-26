import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

app.app_context().push()


def rollback_recredit_too_early_18(deposit: finance_models.Deposit) -> None:
    """
    Rollback a deposit that has a recredit too early.
    """
    recredits = deposit.recredits
    for recredit in recredits:
        if recredit.recreditType == finance_models.RecreditType.RECREDIT_18:
            recredited_amount = recredit.amount
            deposit.amount -= recredited_amount
            logger.info("Un-recredit %s from deposit %s", recredited_amount, deposit.id)
            db.session.delete(recredit)
            db.session.add(deposit)


def run() -> None:
    deposit_query = finance_models.Deposit.query.filter(
        finance_models.Deposit.recredits.any(recreditType=finance_models.RecreditType.RECREDIT_18)
    )
    for deposit in deposit_query:
        with transaction():
            logger.info("Rollback recredit too early 18 for User %s (deposit %s)", deposit.user.id, deposit.id)
            rollback_recredit_too_early_18(deposit)


if __name__ == "__main__":

    run()
    logger.info("Done")
