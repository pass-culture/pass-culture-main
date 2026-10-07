"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41967-auto-ask-for-disability-bonus \
  -f NAMESPACE=recover_disability_bonuses \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import not_
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload

from pcapi.connectors.api_particulier import RATE_LIMIT_TIME_WINDOW_SIZE
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.subscription.bonus.constants import AUTOMATIC_ORIGIN
from pcapi.core.subscription.bonus.fraud_check_api import create_disability_bonus_credit_fraud_checks
from pcapi.core.subscription.models import BeneficiaryFraudCheck
from pcapi.core.subscription.models import FraudCheckType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.settings import PARTICULIER_API_RATE_LIMIT_THRESHOLD
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

PAGE_SIZE = 500


def create_disability_fraud_checks_retroactively(
    from_deposit_id: int, apply: bool, page_size: int = PAGE_SIZE, max_page: int | None = None
) -> None:
    credit_v3_stmt = (
        select(Deposit)
        .where(
            Deposit.type == DepositType.GRANT_17_18,
            Deposit.recredits.any(Recredit.recreditType == RecreditType.RECREDIT_18),
            not_(Deposit.recredits.any(Recredit.recreditType == RecreditType.BONUS_CREDIT)),
        )
        .options(selectinload(Deposit.recredits), joinedload(Deposit.user).selectinload(User.beneficiaryFraudChecks))
    )

    current_page = 0
    total_created_fraud_checks = 0
    while True:
        current_page += 1
        with atomic():
            keyset_paginated_stmt = (
                credit_v3_stmt.where(Deposit.id > from_deposit_id).order_by(Deposit.id).limit(page_size)
            )
            deposits = db.session.scalars(keyset_paginated_stmt).all()

            if not deposits:
                break

            for deposit in deposits:
                next_retry_at = compute_next_retry_at(total_created_fraud_checks)
                created_fraud_checks = maybe_create_disability_bonus_credits_attempts(deposit.user, next_retry_at)
                if created_fraud_checks:
                    total_created_fraud_checks += len(created_fraud_checks)

            from_deposit_id = deposits[-1].id
            logger.info("Recovered up to deposit %s", from_deposit_id)

            if apply:
                logger.info("Commiting")
            else:
                logger.info("Rolling back")
                mark_transaction_as_invalid()

        if max_page is not None and current_page >= max_page:
            logger.info("Exiting after reaching page %s", current_page)
            break

    logger.info("%s disability fraud checks were created", total_created_fraud_checks)


def compute_next_retry_at(total_created: int) -> datetime:
    # spreading the recovery timings across time allows human trafic retries during the recovery period
    STARVATION_MARGIN = 1.2
    offset = total_created / PARTICULIER_API_RATE_LIMIT_THRESHOLD * RATE_LIMIT_TIME_WINDOW_SIZE

    return get_naive_utc_now() + relativedelta(seconds=int(offset * STARVATION_MARGIN))


def maybe_create_disability_bonus_credits_attempts(
    user: User, next_retry_at: datetime
) -> tuple[BeneficiaryFraudCheck, BeneficiaryFraudCheck] | None:
    deposit = user.deposit
    if not deposit:
        logger.error("User %s has no deposit", user.id)
        return None

    if user.received_bonus_credit:
        logger.warning(
            "Bonus credit exclusion did not work and user %s with deposit %s got included", user.id, deposit.id
        )
        return None

    DISABILITY_TYPES = [FraudCheckType.AAH_BONUS_CREDIT, FraudCheckType.AEEH_BONUS_CREDIT]
    fraud_check_types = [fraud_check.type for fraud_check in user.beneficiaryFraudChecks]
    if any(disability_type in fraud_check_types for disability_type in DISABILITY_TYPES):
        return None

    return create_disability_bonus_credit_fraud_checks(
        user,
        origin=f"{AUTOMATIC_ORIGIN} (PC-41967) Rattrapage massif des demandes de bonification handicap",
        next_retry_at=next_retry_at,
    )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--from-deposit-id", type=int, default=6352934)
    parser.add_argument("--page-size", type=int)
    parser.add_argument("--max-page", type=int)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    create_disability_fraud_checks_retroactively(
        args.from_deposit_id, args.apply, args.page_size or PAGE_SIZE, args.max_page
    )

    logger.info("Finished")
