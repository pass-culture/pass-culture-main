from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import eligibility_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils


def has_failed_phone_validation(user: users_models.User) -> bool:
    # user.beneficiaryFraudChecks should have been joinedloaded before to reduce the number of db requests
    return any(
        fraud_check.status == fraud_models.FraudCheckStatus.KO
        and fraud_check.type == fraud_models.FraudCheckType.PHONE_VALIDATION
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
        return sorted_reviews[0].review == fraud_models.FraudReviewStatus.KO

    return False


def get_latest_completed_profile_check(user: users_models.User) -> fraud_models.BeneficiaryFraudCheck | None:
    if profile_completion_checks := _get_completed_profile_checks(user):
        # user.beneficiaryFraudChecks are sorted by ascending dateCreated
        return profile_completion_checks[-1]

    return None


def get_completed_profile_check(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> fraud_models.BeneficiaryFraudCheck | None:
    profile_completion_checks = _get_completed_profile_checks(user)

    relevant_checks = [
        fraud_check
        for fraud_check in profile_completion_checks
        if _is_fraud_check_relevant_for_eligibility(fraud_check, eligibility)
    ]
    if relevant_checks:
        return relevant_checks[0]

    return None


def get_completed_underage_profile_check(user: users_models.User) -> fraud_models.BeneficiaryFraudCheck | None:
    profile_completion_checks = _get_completed_profile_checks(user)

    relevant_checks = [
        fraud_check for fraud_check in profile_completion_checks if _is_fraud_check_relevant_for_underage(fraud_check)
    ]
    if relevant_checks:
        return relevant_checks[0]

    return None


def _get_completed_profile_checks(user: users_models.User) -> list[fraud_models.BeneficiaryFraudCheck]:
    """
    This function assumes that the user.beneficiaryFraudChecks relationship is already loaded to avoid additional
    queries.

    Example: db.session.query(User).options(selectinload(User.beneficiaryFraudChecks))
    """
    return [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        and fraud_check.status == fraud_models.FraudCheckStatus.OK
    ]


def get_filled_dms_fraud_check(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> fraud_models.BeneficiaryFraudCheck | None:
    """
    If a pending or started DMS fraud check exists, the user has already completed their profile.
    """
    filled_dms_fraud_checks = _get_filled_pending_or_started_dms_fraud_checks(user)

    relevant_checks = [
        fraud_check
        for fraud_check in filled_dms_fraud_checks
        if _is_fraud_check_relevant_for_eligibility(fraud_check, eligibility)
    ]
    if relevant_checks:
        return relevant_checks[0]

    return None


def get_filled_underage_dms_fraud_check(user: users_models.User) -> fraud_models.BeneficiaryFraudCheck | None:
    """
    If a pending or started DMS fraud check exists, the user has already completed their profile.
    """
    filled_dms_fraud_checks = _get_filled_pending_or_started_dms_fraud_checks(user)

    relevant_checks = [
        fraud_check for fraud_check in filled_dms_fraud_checks if _is_fraud_check_relevant_for_underage(fraud_check)
    ]
    if relevant_checks:
        return relevant_checks[0]

    return None


def _get_filled_pending_or_started_dms_fraud_checks(
    user: users_models.User,
) -> list[fraud_models.BeneficiaryFraudCheck]:
    """
    This function assumes that the user.beneficiaryFraudChecks relationship is already loaded to avoid additional
    queries.

    Example: db.session.query(User).options(selectinload(User.beneficiaryFraudChecks))
    """
    return [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == fraud_models.FraudCheckType.DMS
        and fraud_check.status in (fraud_models.FraudCheckStatus.PENDING, fraud_models.FraudCheckStatus.STARTED)
        and fraud_check.resultContent
        and fraud_check.source_data().city is not None
    ]


def get_relevant_identity_fraud_check(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> fraud_models.BeneficiaryFraudCheck | None:
    """
    This function assumes that the user.beneficiaryFraudChecks relationship is already loaded to avoid additional
    queries.

    Example: db.session.query(User).options(selectinload(User.beneficiaryFraudChecks))
    """
    identity_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in fraud_models.IDENTITY_CHECK_TYPES
        and _is_identity_fraud_check_relevant_for_eligibility(fraud_check, eligibility)
    ]
    identity_fraud_checks.sort(key=lambda fraud_check: fraud_check.dateCreated, reverse=True)

    if not identity_fraud_checks:
        return None

    for status in (  # order matters here
        fraud_models.FraudCheckStatus.OK,
        fraud_models.FraudCheckStatus.PENDING,
        fraud_models.FraudCheckStatus.STARTED,
        fraud_models.FraudCheckStatus.SUSPICIOUS,
        fraud_models.FraudCheckStatus.KO,
    ):
        relevant_fraud_check = next(
            (fraud_check for fraud_check in identity_fraud_checks if fraud_check.status == status), None
        )
        if relevant_fraud_check:
            return relevant_fraud_check

    return None


def _is_identity_fraud_check_relevant_for_eligibility(
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    eligibility: users_models.EligibilityType | None,
) -> bool:
    if fraud_check.is_id_check_ok_across_eligibilities_or_age:
        return eligibility in fraud_check.applicable_eligibilities

    if users_models.EligibilityType.AGE17_18 in (eligibility, fraud_check.eligibilityType):
        return _is_fraud_check_relevant_for_age(fraud_check)

    return eligibility in fraud_check.applicable_eligibilities


def get_completed_honor_statement(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> fraud_models.BeneficiaryFraudCheck | None:
    """
    This function assumes that the user.beneficiaryFraudChecks relationship is already loaded to avoid additional
    queries.

    Example: db.session.query(User).options(selectinload(User.beneficiaryFraudChecks))
    """
    completed_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == fraud_models.FraudCheckType.HONOR_STATEMENT
        and fraud_check.status == fraud_models.FraudCheckStatus.OK
        and _is_fraud_check_relevant_for_eligibility(fraud_check, eligibility)
    ]

    if completed_fraud_checks:
        return completed_fraud_checks[0]

    return None


def _is_fraud_check_relevant_for_eligibility(
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    eligibility: users_models.EligibilityType | None,
) -> bool:
    if users_models.EligibilityType.AGE17_18 in (eligibility, fraud_check.eligibilityType):
        return _is_fraud_check_relevant_for_age(fraud_check)

    return fraud_check.eligibilityType == eligibility


def _is_fraud_check_relevant_for_age(fraud_check: fraud_models.BeneficiaryFraudCheck) -> bool:
    current_age = fraud_check.user.age
    if not current_age:
        return False

    if current_age < 18:
        return _is_fraud_check_relevant_for_underage(fraud_check)

    return _is_fraud_check_relevant_for_18_or_above(fraud_check)


def _is_fraud_check_relevant_for_underage(fraud_check: fraud_models.BeneficiaryFraudCheck) -> bool:
    age_at_fraud_check = _get_age_at_fraud_check(fraud_check)
    if age_at_fraud_check is None:
        return False
    return eligibility_api.is_underage_eligibility(fraud_check.eligibilityType, age_at_fraud_check)


def _is_fraud_check_relevant_for_18_or_above(
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> bool:
    age_at_fraud_check = _get_age_at_fraud_check(fraud_check)
    if age_at_fraud_check is None:
        return False
    return eligibility_api.is_18_or_above_eligibility(fraud_check.eligibilityType, age_at_fraud_check)


def _get_age_at_fraud_check(fraud_check: fraud_models.BeneficiaryFraudCheck) -> int | None:
    user = fraud_check.user
    if not user.birth_date:
        return None

    known_birthdate_at_fraud_check = eligibility_api.get_known_birthday_at_date(
        fraud_check.user, fraud_check.dateCreated
    )
    if known_birthdate_at_fraud_check is None:
        known_birthdate_at_fraud_check = user.birth_date

    return users_utils.get_age_at_date(known_birthdate_at_fraud_check, fraud_check.dateCreated, user.departementCode)
