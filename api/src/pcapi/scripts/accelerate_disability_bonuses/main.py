"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-44375-accelerate-aah-aeeh \
  -f NAMESPACE=accelerate_disability_bonuses \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import DateTime
from sqlalchemy import select

from pcapi.core.subscription.bonus.constants import AUTOMATIC_ORIGIN
from pcapi.core.subscription.models import BeneficiaryFraudCheck
from pcapi.core.subscription.models import FraudCheckStatus
from pcapi.core.subscription.models import FraudCheckType
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

PAGE_SIZE = 1_000
PREVIOUS_STARVATION_MARGIN = 4.5
NEW_STARVATION_MARGIN = 2


def accelerate_disability_bonuses(apply: bool, page_size: int = PAGE_SIZE, max_page: int | None = None) -> None:
    now = get_naive_utc_now()
    started_disability_fraud_check_stmt = select(BeneficiaryFraudCheck).where(
        BeneficiaryFraudCheck.type.in_([FraudCheckType.AAH_BONUS_CREDIT, FraudCheckType.AEEH_BONUS_CREDIT]),
        BeneficiaryFraudCheck.status == FraudCheckStatus.STARTED,
        BeneficiaryFraudCheck.resultContent.is_not(None),
        BeneficiaryFraudCheck.resultContent["next_retry_at"].astext.cast(DateTime) > now,
        BeneficiaryFraudCheck.reason.is_not(None),
        BeneficiaryFraudCheck.reason.startswith(AUTOMATIC_ORIGIN),
    )

    last_id = 0
    current_page = 0
    while True:
        with atomic():
            keyset_paginated_stmt = (
                started_disability_fraud_check_stmt.where(BeneficiaryFraudCheck.id > last_id)
                .order_by(BeneficiaryFraudCheck.id)
                .limit(page_size)
            )
            started_fraud_checks = db.session.scalars(keyset_paginated_stmt).all()

            if not started_fraud_checks:
                break

            for fraud_check in started_fraud_checks:
                if not fraud_check.resultContent:
                    logger.warning("missing result content for fraud check %s", fraud_check.id)
                    continue

                next_retry_at = fraud_check.resultContent["next_retry_at"]
                created_at = fraud_check.dateCreated

                new_next_retry_at = (
                    created_at + (next_retry_at - created_at) / PREVIOUS_STARVATION_MARGIN * NEW_STARVATION_MARGIN
                )
                fraud_check.resultContent["next_retry_at"] = new_next_retry_at
                logger.info(
                    "updated fraud check %s next_retry_at from %s to %s",
                    fraud_check.id,
                    next_retry_at,
                    new_next_retry_at,
                )

            last_id = started_fraud_checks[-1].id
            logger.info("accelerated fraud checks up to id %s", last_id)

            if apply:
                logger.info("committing")
            else:
                mark_transaction_as_invalid()
                logger.info("rolling back")

        current_page += 1
        if max_page is not None and current_page >= max_page:
            logger.info("Exiting after reaching page %s", current_page)
            break


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--page-size", type=int)
    parser.add_argument("--max-page", type=int)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    accelerate_disability_bonuses(args.apply, args.page_size or PAGE_SIZE, args.max_page)

    logger.info("finished")
