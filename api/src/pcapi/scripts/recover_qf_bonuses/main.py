"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-44078-recover-qf \
  -f NAMESPACE=recover_qf_bonuses \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from pcapi.core.finance.models import Deposit
from pcapi.core.subscription.models import BeneficiaryFraudCheck
from pcapi.core.subscription.models import FraudCheckStatus
from pcapi.core.subscription.models import FraudCheckType
from pcapi.core.subscription.models import FraudReasonCode
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

PAGE_SIZE = 500


def recover_qf_bonus_checks(
    from_fraud_check_id: int, apply: bool, page_size: int = PAGE_SIZE, max_page: int | None = None
) -> None:
    ko_qf_stmt = (
        select(BeneficiaryFraudCheck)
        .where(
            BeneficiaryFraudCheck.type == FraudCheckType.QF_BONUS_CREDIT,
            BeneficiaryFraudCheck.status == FraudCheckStatus.KO,
            BeneficiaryFraudCheck.reasonCodes.contains([FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]),
        )
        .options(joinedload(BeneficiaryFraudCheck.user).selectinload(User.deposits).selectinload(Deposit.recredits))
    )

    current_page = 0
    total_reset = 0
    while True:
        current_page += 1
        with atomic():
            keyset_paginated_stmt = (
                ko_qf_stmt.where(BeneficiaryFraudCheck.id > from_fraud_check_id)
                .order_by(BeneficiaryFraudCheck.id)
                .limit(page_size)
            )
            fraud_checks = db.session.scalars(keyset_paginated_stmt).unique().all()

            if not fraud_checks:
                break

            from_fraud_check_id = fraud_checks[-1].id
            for fraud_check in fraud_checks:
                fraud_check.status = FraudCheckStatus.STARTED
                logger.info("Reset fraud check %s to STARTED", fraud_check.id)

                total_reset += 1

            logger.info("Recovered up to fraud check %s", from_fraud_check_id)

            if apply:
                logger.info("Commiting")
            else:
                logger.info("Rolling back")
                mark_transaction_as_invalid()

        if max_page is not None and current_page >= max_page:
            logger.info("Exiting after reaching page %s", current_page)
            break

    logger.info("%s QF bonus fraud checks were reset to STARTED", total_reset)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--from-fraud-check-id", type=int, default=31000000)
    parser.add_argument("--page-size", type=int)
    parser.add_argument("--max-page", type=int)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    recover_qf_bonus_checks(args.from_fraud_check_id, args.apply, args.page_size or PAGE_SIZE, args.max_page)

    logger.info("Finished")
