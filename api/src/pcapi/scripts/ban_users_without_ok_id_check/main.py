from argparse import ArgumentParser
import logging

from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.fraud.models import BeneficiaryFraudReview
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudReviewStatus
from pcapi.core.fraud.repository import get_relevant_identity_fraud_check
from pcapi.core.users.api import suspend_account
from pcapi.core.users.constants import SuspensionReason
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.settings import CREDIT_V3_DECREE_DATETIME


logger = logging.getLogger(__name__)


class UnknownDepositType(Exception):
    pass


def ban_beneficiaries_without_ok_id_check(is_not_dry_run: bool) -> None:
    logger.info("starting ban_beneficiaries_without_ok_id_check")

    users = _get_beneficiaries_without_ok_id_check()

    for user in users:
        logger.info("Suspending user %s", user.id)
        if is_not_dry_run:
            suspend_account(
                user,
                reason=SuspensionReason.END_OF_ELIGIBILITY,
                comment="(PC-35030) Compte crédité alors que la vérification d'identité n'était pas concluante",
                actor=None,
            )


def _get_beneficiaries_without_ok_id_check() -> list[User]:
    users_query = User.query.filter(
        User.isActive.is_(True),
        Deposit.query.filter(
            Deposit.userId == User.id,
            # select id from deposit where deposit."dateCreated" > '2025-03-03' order by id limit 1;
            Deposit.id > 6362356,
        ).exists(),
    ).options(
        selectinload(User.deposits),
        selectinload(User.beneficiaryFraudChecks),
        selectinload(User.beneficiaryFraudReviews),
    )

    users_to_ban = []
    for user in users_query.yield_per(1000):
        try:
            should_be_banned = not _has_ok_id_check_or_review(user)
            if should_be_banned:
                users_to_ban.append(user)
        except UnknownDepositType:
            logger.error("Unknown deposit type found in user %s", user.id)

    return users_to_ban


def _has_ok_id_check_or_review(user: User) -> bool:
    deposit = user.deposit
    if not deposit:  # do not ban users that do not have a deposit
        return True

    eligibility = _get_activated_eligibility(deposit.type)
    id_fraud_check = get_relevant_identity_fraud_check(user, eligibility)
    if id_fraud_check is not None and id_fraud_check.status == FraudCheckStatus.OK:
        return True

    manual_review = _get_relevant_manual_review(user, eligibility)
    if manual_review is not None and manual_review.review == FraudReviewStatus.OK:
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
            raise UnknownDepositType(f"{deposit_type}")


def _get_relevant_manual_review(user: User, eligibility: EligibilityType) -> BeneficiaryFraudReview | None:
    fraud_reviews = [review for review in user.beneficiaryFraudReviews if review.eligibilityType == eligibility]
    sorted_reviews = sorted(
        fraud_reviews,
        key=lambda fraud_review: fraud_review.dateReviewed,
        reverse=True,
    )
    if not sorted_reviews:
        return None

    relevant_fraud_review = next((review for review in fraud_reviews if review.review == FraudReviewStatus.OK), None)
    if relevant_fraud_review:
        return relevant_fraud_review

    return sorted_reviews[0]


if __name__ == "__main__":
    app.app_context().push()

    parser = ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    ban_beneficiaries_without_ok_id_check(args.not_dry)
