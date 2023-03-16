from pcapi.core.users import models as users_models

from . import models


def get_last_user_profiling_fraud_check(user: users_models.User) -> models.BeneficiaryFraudCheck | None:
    # User profiling is not performed for UNDERAGE credit, no need to filter on eligibilityType here

    sorted_fraud_checks = sorted(
        [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == models.FraudCheckType.USER_PROFILING
        ],
        key=lambda fraud_check: fraud_check.dateCreated,
        reverse=True,
    )

    if sorted_fraud_checks:
        return sorted_fraud_checks[0]

    return None


def has_failed_phone_validation(user: users_models.User) -> bool:
    return any(
        fraud_check.status == models.FraudCheckStatus.KO and fraud_check.type == models.FraudCheckType.PHONE_VALIDATION
        for fraud_check in user.beneficiaryFraudChecks
    )


def has_admin_ko_review(user: users_models.User) -> bool:
    sorted_reviews = sorted(
        [fraud_review for fraud_review in user.beneficiaryFraudReviews],
        key=lambda fraud_review: fraud_review.dateReviewed,
        reverse=True,
    )

    if sorted_reviews:
        return sorted_reviews[0].review == models.FraudReviewStatus.KO

    return False
