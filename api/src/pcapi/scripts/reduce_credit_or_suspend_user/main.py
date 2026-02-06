"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-35179-reduce-users-credit-or-suspend \
  -f NAMESPACE=reduce_credit_or_suspend_user \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import decimal
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import conf as finance_conf
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import transaction_manager


logger = logging.getLogger(__name__)


def reduce_or_expire_user_credit(should_update_external_user: bool, author_id: int) -> None:
    total_deposits_expired = 0
    total_surplus_money_spent = decimal.Decimal("0")

    users_with_duplicate_recredit_stmt = (
        sa.select(users_models.User)
        .join(users_models.User.deposits)
        .join(finance_models.Deposit.recredits)
        .where(finance_models.Recredit.recreditType == finance_models.RecreditType.RECREDIT_17)
        .group_by(users_models.User.id)
        .having(sa.func.count() > 1)
    )
    users_with_duplicate_recredit = db.session.scalars(users_with_duplicate_recredit_stmt).all()
    for user in users_with_duplicate_recredit:
        domains_credit = users_api.get_domains_credit(user)
        if not domains_credit:
            logger.error("no credit found for user %s", user.id)
            continue

        can_reduce_credit = domains_credit.all.remaining >= finance_conf.GRANTED_DEPOSIT_AMOUNT_17_v3
        if can_reduce_credit:
            continue
            # _reduce_user_deposit(user, author_id)
            #
            # logger.info("reduced credit of user %s", user.id)
        else:
            _expire_user_deposit(user, author_id)

            surplus_money_spent = finance_conf.GRANTED_DEPOSIT_AMOUNT_17_v3 - domains_credit.all.remaining
            logger.info(
                "expired user %s deposit that got away with a surplus of %d euros",
                user.id,
                surplus_money_spent,
                extra={"user_id": user.id, "surplus_money_spent": surplus_money_spent},
            )

            total_deposits_expired += 1
            total_surplus_money_spent += surplus_money_spent

        # if should_update_external_user:
        #     external_attributes_api.update_external_user(user)

    logger.info("----- Overview -----")

    total_users = len(users_with_duplicate_recredit)
    logger.info(
        "%d users were granted the RECREDIT_17 twice",
    )

    total_credits_reduced = total_users - total_deposits_expired
    logger.info(
        "successfully took away the surplus credit from %d users (%.2f%%)",
        total_credits_reduced,
        100 * total_credits_reduced / total_users if total_users else 100,
    )

    logger.info(
        "expired the credits of %d users (%.2f%%), losing a total of %.2f euros given in excess",
        total_deposits_expired,
        100 * total_deposits_expired / total_users if total_users else 100,
        total_surplus_money_spent,
    )


def _reduce_user_deposit(user: users_models.User, author_id: int) -> None:
    deposit = user.deposit
    if not deposit:
        logger.error("no deposit found for user %s", user.id)
        return

    if deposit.type != finance_models.DepositType.GRANT_17_18:
        logger.error("the deposit to reduce should be of type GRANT_17_18, not %s", deposit.type.value)
        return

    age_17_recredits = [
        recredit for recredit in deposit.recredits if recredit.recreditType == finance_models.RecreditType.RECREDIT_17
    ]
    if not age_17_recredits:
        logger.error("no age 17 recredit found in user %s deposit %s", user.id, deposit.id)
        return

    age_17_recredit = age_17_recredits[0]

    reverse_amount = -age_17_recredit.amount
    reverse_recredit = finance_models.Recredit(
        deposit=deposit,
        amount=reverse_amount,
        recreditType=finance_models.RecreditType.MANUAL_MODIFICATION,
        comment="(PC-40031) Retrait du crédit de 50€ donné par erreur alors que le jeune a été déjà été crédité de 30€ pour ses 17 ans",
    )
    deposit.amount += reverse_recredit.amount

    db.session.add(reverse_recredit)


def _expire_user_deposit(user: users_models.User, author_id: int) -> None:
    deposit = user.deposit
    if not deposit:
        logger.error("no deposit found for user %s", user.id)
        return

    if deposit.type != finance_models.DepositType.GRANT_17_18:
        logger.error("the deposit to expire should be of type GRANT_17_18, not %s", deposit.type.value)
        return

    deposit.expirationDate = datetime.datetime.now(tz=None)

    action_log = history_models.ActionHistory(
        actionType=history_models.ActionType.COMMENT,
        user=user,
        authorUserId=author_id,
        comment="(PC-40031) Expiration du crédit car le surplus de 50€ donné par erreur ne peut pas être retiré",
    )
    db.session.add(action_log)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--author-id", type=int)
    args = parser.parse_args()

    with transaction_manager.atomic():
        db.session.execute(sa.text("set session statement_timeout = '300s'"))

        if not args.not_dry:
            transaction_manager.mark_transaction_as_invalid()
            logger.info("marking the transaction as invalid because of dry run")

        reduce_or_expire_user_credit(should_update_external_user=args.not_dry, author_id=args.author_id)
