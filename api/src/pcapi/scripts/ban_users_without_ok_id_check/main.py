from argparse import ArgumentParser
import logging

from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudReviewStatus
from pcapi.core.fraud.models import BeneficiaryFraudReview
from pcapi.core.fraud.repository import get_relevant_identity_fraud_check
from pcapi.core.users.api import suspend_account
from pcapi.core.users.constants import SuspensionReason
from pcapi.core.users.models import User
from pcapi.core.users.models import EligibilityType
from pcapi.models import db
from pcapi.settings import CREDIT_V3_DECREE_DATETIME


logger = logging.getLogger(__name__)


def ban_beneficiaries_without_ok_id_check(is_not_dry_run: bool) -> None:
    users = _get_beneficiaries_without_ok_id_check()

    for user in users:
        logger.info("Suspending user %s", user.id)
        if is_not_dry_run:
            suspend_account(
                user,
                reason=SuspensionReason.FRAUD_SUSPICION,
                comment="(PC-35030) Compte crédité alors que la vérification d'identité n'était pas concluante",
                actor=None,
            )


def _get_beneficiaries_without_ok_id_check() -> list[User]:
    users = (
        User.query.filter(
            Deposit.query.filter(
                Deposit.userId == User.id,
                Deposit.dateCreated > CREDIT_V3_DECREE_DATETIME,
            ).exists()
        )
        .options(
            selectinload(User.deposits),
            selectinload(User.beneficiaryFraudChecks),
            selectinload(User.beneficiaryFraudReviews),
        )
        .all()
    )

    return [user for user in users if not _has_ok_id_check(user)]


def _has_ok_id_check(user: User) -> bool:
    deposit = user.deposit
    if not deposit:
        return True

    eligibility = _get_activated_eligibility(deposit.type)
    id_fraud_check = get_relevant_identity_fraud_check(user, eligibility)
    if id_fraud_check is not None and id_fraud_check.status == FraudCheckStatus.OK:
        return True

    manual_review = _get_relevant_manual_review(user, eligibility)
    if manual_review is not None and manual_review.status == FraudReviewStatus.OK:
        return True

    return False


def _get_activated_eligibility(deposit_type: DepositType) -> EligibilityType:
    match deposit_type:
        case DepositType.GRANT_17_18:
            return EligibilityType.AGE17_18
        case DepositType.GRANT_15_17:
            return EligibilityType.UNDERAGE
        case DepositType.GRANT_18:
            return EligibilityType.AGE18
        case _:
            raise ValueError(f"Unknown deposit type {deposit_type}")


def _get_relevant_manual_review(user: User, eligibility: EligibilityType) -> BeneficiaryFraudReview | None:
    relevant_fraud_reviews = [
        review for review in user.beneficiaryFraudReviews if review.eligibilityType == eligibility
    ]
    sorted_reviews = sorted(
        relevant_fraud_reviews,
        key=lambda fraud_review: fraud_review.dateReviewed,
        reverse=True,
    )
    if sorted_reviews:
        return sorted_reviews[0]

    return None


if __name__ == "__main__":
    app.app_context().push()

    parser = ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    ban_beneficiaries_without_ok_id_check(args.not_dry)
