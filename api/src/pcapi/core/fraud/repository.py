from pcapi.core.users import models as users_models

from . import models


def has_failed_phone_validation(user: users_models.User) -> bool:
    # user.beneficiaryFraudChecks should have been joinedloaded before to reduce the number of db requests
    return any(
        fraud_check.status == models.FraudCheckStatus.KO and fraud_check.type == models.FraudCheckType.PHONE_VALIDATION
        for fraud_check in user.beneficiaryFraudChecks
    )


def has_admin_ko_review(user: users_models.User) -> bool:
    # user.beneficiaryFraudReviews should have been joinedloaded before to reduce the number of db requests
    sorted_reviews = sorted(
        user.beneficiaryFraudReviews,
        key=lambda fraud_review: fraud_review.dateReviewed,
        reverse=True,
    )

    if sorted_reviews:
        return sorted_reviews[0].review == models.FraudReviewStatus.KO

    return False
