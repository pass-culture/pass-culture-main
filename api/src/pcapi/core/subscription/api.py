import datetime
import logging
import typing

from pcapi import settings
import pcapi.core.fraud.api as fraud_api
from pcapi.core.fraud.common import models as common_fraud_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.repository as fraud_repository
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.payments import api as payments_api
from pcapi.core.payments import exceptions as payments_exceptions
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
import pcapi.repository as pcapi_repository
import pcapi.utils.postal_code as postal_code_utils
from pcapi.workers import apps_flyer_job

from . import exceptions
from . import models
from . import repository


logger = logging.getLogger(__name__)

USER_PROFILING_BLOCKING_STATUS = fraud_models.FraudCheckStatus.KO


def _get_age_at_first_registration(user: users_models.User, eligibility: users_models.EligibilityType) -> int | None:
    first_registration_date = get_first_registration_date(user, user.birth_date, eligibility)
    if not first_registration_date or not user.birth_date:
        return None
    return users_utils.get_age_at_date(user.birth_date, first_registration_date)


def activate_beneficiary_for_eligibility(
    user: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
) -> users_models.User:
    if eligibility == users_models.EligibilityType.UNDERAGE:
        user.add_underage_beneficiary_role()
        age_at_registration = _get_age_at_first_registration(user, users_models.EligibilityType.UNDERAGE)

        if age_at_registration not in users_constants.ELIGIBILITY_UNDERAGE_RANGE:
            raise exceptions.InvalidAgeException(age=age_at_registration)

    elif eligibility == users_models.EligibilityType.AGE18:
        user.add_beneficiary_role()
        user.remove_underage_beneficiary_role()
        age_at_registration = users_constants.ELIGIBILITY_AGE_18
    else:
        raise exceptions.InvalidEligibilityTypeException()

    deposit = payments_api.create_deposit(
        user,
        deposit_source=deposit_source,
        eligibility=eligibility,
        age_at_registration=age_at_registration,
    )

    db.session.add_all((user, deposit))
    db.session.commit()
    logger.info("Activated beneficiary and created deposit", extra={"user": user.id, "source": deposit_source})

    is_email_sent = transactional_mails.send_accepted_as_beneficiary_email(user=user)
    if not is_email_sent:
        logger.warning("Could not send accepted as beneficiary email to user", extra={"user": user.id})

    users_external.update_external_user(user)

    if "apps_flyer" in user.externalIds:  # type: ignore [operator]
        apps_flyer_job.log_user_becomes_beneficiary_event_job.delay(user.id)

    return user


def _get_filled_dms_fraud_check(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> fraud_models.BeneficiaryFraudCheck | None:
    # If a pending or started DMS fraud check exists, the user has already completed the profile.
    # No need to ask for this information again.
    return next(
        (
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.DMS
            and fraud_check.eligibilityType == eligibility
            and fraud_check.status in (fraud_models.FraudCheckStatus.PENDING, fraud_models.FraudCheckStatus.STARTED)
            and fraud_check.resultContent
            and fraud_check.source_data().city is not None
        ),
        None,
    )


def has_completed_profile_for_given_eligibility(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> bool:
    if repository.get_completed_profile_check(user, eligibility) is not None:
        return True
    if _get_filled_dms_fraud_check(user, eligibility) is not None:
        return True
    return False


def get_declared_names(user: users_models.User) -> typing.Tuple[str, str] | None:
    profile_completion_check = repository.get_completed_profile_check(user, user.eligibility)
    if profile_completion_check and profile_completion_check.resultContent:
        profile_data = typing.cast(fraud_models.ProfileCompletionContent, profile_completion_check.source_data())
        return profile_data.first_name, profile_data.last_name

    dms_filled_check = _get_filled_dms_fraud_check(user, user.eligibility)
    if dms_filled_check:
        dms_data = typing.cast(fraud_models.DMSContent, dms_filled_check.source_data())
        return dms_data.first_name, dms_data.last_name

    return None


def is_eligibility_activable(user: users_models.User, eligibility: users_models.EligibilityType | None) -> bool:
    return (
        user.eligibility == eligibility
        and users_api.is_eligible_for_beneficiary_upgrade(user, eligibility)
        and users_api.is_user_age_compatible_with_eligibility(user.age, eligibility)
    )


def get_email_validation_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if user.isEmailValidated:
        status = models.SubscriptionItemStatus.OK
    else:
        if is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.EMAIL_VALIDATION, status=status)


def get_phone_validation_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if eligibility != users_models.EligibilityType.AGE18:
        status = models.SubscriptionItemStatus.NOT_APPLICABLE
    else:
        if user.is_phone_validated:
            status = models.SubscriptionItemStatus.OK
        elif user.is_phone_validation_skipped:
            status = models.SubscriptionItemStatus.SKIPPED
        elif not FeatureToggle.ENABLE_PHONE_VALIDATION.is_active():
            status = models.SubscriptionItemStatus.NOT_ENABLED
        elif fraud_repository.has_failed_phone_validation(user):
            status = models.SubscriptionItemStatus.KO
        elif is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PHONE_VALIDATION, status=status)


def _should_validate_phone(user: users_models.User, eligibility: users_models.EligibilityType | None) -> bool:
    phone_subscription_item = get_phone_validation_subscription_item(user, eligibility)
    return phone_subscription_item.status in (models.SubscriptionItemStatus.TODO, models.SubscriptionItemStatus.KO)


def get_user_profiling_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if eligibility != users_models.EligibilityType.AGE18:
        status = models.SubscriptionItemStatus.NOT_APPLICABLE
    else:
        user_profiling = fraud_repository.get_last_user_profiling_fraud_check(user)
        if user_profiling:
            if user_profiling.status == fraud_models.FraudCheckStatus.OK:
                status = models.SubscriptionItemStatus.OK
            elif user_profiling.status == USER_PROFILING_BLOCKING_STATUS:
                status = models.SubscriptionItemStatus.KO
            elif user_profiling.status == fraud_models.FraudCheckStatus.SUSPICIOUS:
                status = models.SubscriptionItemStatus.SUSPICIOUS
            else:
                logger.exception("Unexpected UserProfiling status %s", user_profiling.status)
                status = models.SubscriptionItemStatus.KO

        elif not FeatureToggle.ENABLE_USER_PROFILING.is_active():
            status = models.SubscriptionItemStatus.NOT_ENABLED

        elif is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.USER_PROFILING, status=status)


def get_profile_completion_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> models.SubscriptionItem:
    if has_completed_profile_for_given_eligibility(user, eligibility):
        status = models.SubscriptionItemStatus.OK
    elif is_eligibility_activable(user, eligibility):
        status = models.SubscriptionItemStatus.TODO
    else:
        status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PROFILE_COMPLETION, status=status)


def _get_identity_fraud_checks_for_eligibility(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> list[fraud_models.BeneficiaryFraudCheck]:
    return [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in fraud_models.IDENTITY_CHECK_TYPES and eligibility in fraud_check.applicable_eligibilities
    ]


def get_identity_check_subscription_status(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    """
    eligibility may be the current user.eligibility or a specific eligibility.
    The result relies on the FraudChecks made with the 3 current identity providers (DMS, Ubble and Educonnect)
    and with the legacy provider (Jouve)
    """
    if eligibility is None:
        return models.SubscriptionItemStatus.VOID  # type: ignore [return-value]

    identity_fraud_checks = _get_identity_fraud_checks_for_eligibility(user, eligibility)

    dms_checks = [check for check in identity_fraud_checks if check.type == fraud_models.FraudCheckType.DMS]
    educonnect_checks = [
        check for check in identity_fraud_checks if check.type == fraud_models.FraudCheckType.EDUCONNECT
    ]
    ubble_checks = [check for check in identity_fraud_checks if check.type == fraud_models.FraudCheckType.UBBLE]
    jouve_checks = [check for check in identity_fraud_checks if check.type == fraud_models.FraudCheckType.JOUVE]

    statuses = [
        dms_subscription_api.get_dms_subscription_item_status(user, eligibility, dms_checks),
        educonnect_subscription_api.get_educonnect_subscription_item_status(user, eligibility, educonnect_checks),
        ubble_subscription_api.get_ubble_subscription_item_status(user, eligibility, ubble_checks),
        _get_jouve_subscription_item_status(user, eligibility, jouve_checks),
    ]

    if any(status == models.SubscriptionItemStatus.OK for status in statuses):
        return models.SubscriptionItemStatus.OK  # type: ignore [return-value]
    if any(status == models.SubscriptionItemStatus.PENDING for status in statuses):
        return models.SubscriptionItemStatus.PENDING  # type: ignore [return-value]
    if any(status == models.SubscriptionItemStatus.KO for status in statuses):
        return models.SubscriptionItemStatus.KO  # type: ignore [return-value]
    if any(status == models.SubscriptionItemStatus.SUSPICIOUS for status in statuses):
        return models.SubscriptionItemStatus.SUSPICIOUS  # type: ignore [return-value]
    if any(status == models.SubscriptionItemStatus.TODO for status in statuses):
        return models.SubscriptionItemStatus.TODO  # type: ignore [return-value]

    return models.SubscriptionItemStatus.VOID  # type: ignore [return-value]


def get_identity_check_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    status = get_identity_check_subscription_status(user, eligibility)
    return models.SubscriptionItem(type=models.SubscriptionStep.IDENTITY_CHECK, status=status)  # type: ignore [arg-type]


def get_honor_statement_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if fraud_api.has_performed_honor_statement(user, eligibility):  # type: ignore [arg-type]
        status = models.SubscriptionItemStatus.OK
    else:
        if is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.HONOR_STATEMENT, status=status)


def get_next_subscription_step(user: users_models.User) -> models.SubscriptionStep | None:
    if not user.isEmailValidated:
        return models.SubscriptionStep.EMAIL_VALIDATION

    if not user.eligibility or not users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility):
        return None

    if fraud_repository.has_admin_ko_review(user):
        return None

    if _should_validate_phone(user, user.eligibility):
        return models.SubscriptionStep.PHONE_VALIDATION

    if user.eligibility == users_models.EligibilityType.AGE18:
        if (
            not (user.is_phone_validated or user.is_phone_validation_skipped)
            and FeatureToggle.ENABLE_PHONE_VALIDATION.is_active()
        ):
            return models.SubscriptionStep.PHONE_VALIDATION

    user_profiling_item = get_user_profiling_subscription_item(user, user.eligibility)

    if user_profiling_item.status == models.SubscriptionItemStatus.TODO:
        return models.SubscriptionStep.USER_PROFILING
    if user_profiling_item.status == models.SubscriptionItemStatus.KO:
        return None

    if not has_completed_profile_for_given_eligibility(user, user.eligibility):
        return models.SubscriptionStep.PROFILE_COMPLETION

    if _needs_to_perform_identity_check(user):
        if not get_allowed_identity_check_methods(user):
            return models.SubscriptionStep.MAINTENANCE
        return models.SubscriptionStep.IDENTITY_CHECK

    if not fraud_api.has_performed_honor_statement(user, user.eligibility):
        return models.SubscriptionStep.HONOR_STATEMENT

    return None


def _needs_to_perform_identity_check(user) -> bool:  # type: ignore [no-untyped-def]
    return get_identity_check_subscription_status(user, user.eligibility) == models.SubscriptionItemStatus.TODO


def complete_profile(
    user: users_models.User,
    address: str,
    city: str,
    postal_code: str,
    activity: str,
    first_name: str,
    last_name: str,
    school_type: users_models.SchoolTypeEnum | None = None,
) -> None:
    update_payload = {
        "address": address,
        "city": city,
        "postalCode": postal_code,
        "departementCode": postal_code_utils.PostalCode(postal_code).get_departement_code(),
        "activity": activity,
        "schoolType": school_type,
    }

    if not user.firstName:
        update_payload["firstName"] = first_name

    if not user.lastName:
        update_payload["lastName"] = last_name

    with pcapi_repository.transaction():
        users_models.User.query.filter(users_models.User.id == user.id).update(update_payload)

    fraud_api.create_profile_completion_fraud_check(
        user,
        user.eligibility,
        fraud_models.ProfileCompletionContent(
            activity=activity,
            city=city,
            first_name=first_name,
            last_name=last_name,
            origin="Completed in application step",
            postalCode=postal_code,
            school_type=school_type,
        ),
    )
    logger.info("User completed profile step", extra={"user": user.id})


def is_identity_check_with_document_method_allowed_for_underage(user: users_models.User) -> bool:

    if not FeatureToggle.ALLOW_IDCHECK_UNDERAGE_REGISTRATION.is_active():
        return False

    if user.schoolType in (
        users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL,
        users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
    ):
        return FeatureToggle.ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE.is_active()
    return True


def get_allowed_identity_check_methods(user: users_models.User) -> list[models.IdentityCheckMethod]:
    allowed_methods = []

    if user.eligibility == users_models.EligibilityType.UNDERAGE:
        if FeatureToggle.ENABLE_EDUCONNECT_AUTHENTICATION.is_active():
            allowed_methods.append(models.IdentityCheckMethod.EDUCONNECT)

        if is_identity_check_with_document_method_allowed_for_underage(user):
            if FeatureToggle.ENABLE_UBBLE.is_active() and _is_ubble_allowed_if_subscription_overflow(user):
                allowed_methods.append(models.IdentityCheckMethod.UBBLE)

    elif user.eligibility == users_models.EligibilityType.AGE18:
        if FeatureToggle.ALLOW_IDCHECK_REGISTRATION.is_active():
            if FeatureToggle.ENABLE_UBBLE.is_active() and _is_ubble_allowed_if_subscription_overflow(user):
                allowed_methods.append(models.IdentityCheckMethod.UBBLE)

    return allowed_methods


def is_phone_validation_in_stepper(user: users_models.User) -> bool:
    return user.eligibility == users_models.EligibilityType.AGE18 and FeatureToggle.ENABLE_PHONE_VALIDATION.is_active()


def _is_ubble_allowed_if_subscription_overflow(user: users_models.User) -> bool:
    if not FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION.is_active():
        return True

    if not user.birth_date:
        return False

    future_age = users_utils.get_age_at_date(
        user.birth_date,
        datetime.datetime.utcnow() + datetime.timedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS),  # type: ignore [arg-type]
    )
    eligibility_ranges = users_constants.ELIGIBILITY_UNDERAGE_RANGE + [users_constants.ELIGIBILITY_AGE_18]
    eligibility_ranges = [age + 1 for age in eligibility_ranges]
    if future_age > user.age and future_age in eligibility_ranges:  # type: ignore [operator]
        return True

    return False


def get_maintenance_page_type(user: users_models.User) -> models.MaintenancePageType | None:
    allowed_identity_check_methods = get_allowed_identity_check_methods(user)
    if allowed_identity_check_methods:
        return None

    if (
        user.eligibility == users_models.EligibilityType.AGE18
        and FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18.is_active()
    ):
        return models.MaintenancePageType.WITH_DMS
    if (
        user.eligibility == users_models.EligibilityType.UNDERAGE
        and FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE.is_active()
    ):
        return models.MaintenancePageType.WITH_DMS

    return models.MaintenancePageType.WITHOUT_DMS


def _get_activable_eligibility(fraud_check: fraud_models.BeneficiaryFraudCheck) -> users_models.EligibilityType | None:
    source_data = typing.cast(common_fraud_models.IdentityCheckContent, fraud_check.source_data())
    birth_date = source_data.get_birth_date()

    if not birth_date:
        return None

    user_age = users_utils.get_age_from_birth_date(birth_date)

    for eligibility in fraud_check.applicable_eligibilities:
        is_activable = users_api.is_eligible_for_beneficiary_upgrade(fraud_check.user, eligibility)
        is_age_compatible = users_api.is_user_age_compatible_with_eligibility(user_age, eligibility)

        if is_activable and is_age_compatible:
            return eligibility

    return None


def _get_activable_identity_check(
    user: users_models.User,
) -> tuple[fraud_models.BeneficiaryFraudCheck, users_models.EligibilityType] | None:
    """Finds latest created activable identity fraud check for a user."""
    identity_fraud_checks = sorted(
        [
            check
            for check in user.beneficiaryFraudChecks
            if check.type in fraud_models.IDENTITY_CHECK_TYPES and check.status == fraud_models.FraudCheckStatus.OK
        ],
        key=lambda fraud_check: fraud_check.dateCreated,
        reverse=True,
    )
    for fraud_check in identity_fraud_checks:
        eligibility = _get_activable_eligibility(fraud_check)
        if eligibility:
            return fraud_check, eligibility

    return None


def _has_completed_other_steps(user: users_models.User, activable_eligibility: users_models.EligibilityType) -> bool:
    if _should_validate_phone(user, activable_eligibility):
        return False

    subscription_item = get_user_profiling_subscription_item(user, activable_eligibility)
    if subscription_item.status in (models.SubscriptionItemStatus.TODO, models.SubscriptionItemStatus.KO):
        return False

    profile_completion = get_profile_completion_subscription_item(user, activable_eligibility)
    if profile_completion.status != models.SubscriptionItemStatus.OK:
        return False

    if not fraud_api.has_performed_honor_statement(user, activable_eligibility):
        return False

    return True


def activate_beneficiary_if_no_missing_step(user: users_models.User) -> bool:
    activable_fraud_check_and_eligibility = _get_activable_identity_check(user)

    if not activable_fraud_check_and_eligibility:
        return False

    activable_fraud_check, activable_eligibility = activable_fraud_check_and_eligibility

    if not _has_completed_other_steps(user, activable_eligibility):
        return False

    fraud_api.invalidate_fraud_check_if_duplicate(activable_fraud_check)

    if activable_fraud_check.status != fraud_models.FraudCheckStatus.OK:
        return False

    source_data = typing.cast(common_fraud_models.IdentityCheckContent, activable_fraud_check.source_data())
    users_api.update_user_information_from_external_source(user, source_data, commit=False)

    try:
        activate_beneficiary_for_eligibility(user, activable_fraud_check.get_detailed_source(), activable_eligibility)
    except (payments_exceptions.DepositTypeAlreadyGrantedException, payments_exceptions.UserHasAlreadyActiveDeposit):
        # this error may happen on identity provider concurrent requests
        logger.info("A deposit already exists for user %s", user.id)
        return False

    return True


DEPRECATED_UBBLE_PREFIX = "deprecated-"


def _update_fraud_check_eligibility_with_history(
    fraud_check: fraud_models.BeneficiaryFraudCheck, eligibility: users_models.EligibilityType
) -> fraud_models.BeneficiaryFraudCheck:
    # Update fraud check by creating a new one with the correct eligibility
    new_fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=fraud_check.user,
        type=fraud_check.type,
        thirdPartyId=fraud_check.thirdPartyId,
        resultContent=fraud_check.resultContent,
        status=fraud_check.status,
        reason=fraud_check.reason,
        reasonCodes=fraud_check.reasonCodes,
        eligibilityType=eligibility,
    )
    # Cancel the old fraud check
    fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
    reason_message = "Eligibility type changed by the identity provider"
    fraud_check.reason = (
        f"{fraud_check.reason} {fraud_api.FRAUD_RESULT_REASON_SEPARATOR} {reason_message}"
        if fraud_check.reason
        else reason_message
    )
    if fraud_check.reasonCodes is None:
        fraud_check.reasonCodes = []
    fraud_check.reasonCodes.append(fraud_models.FraudReasonCode.ELIGIBILITY_CHANGED)
    fraud_check.thirdPartyId = f"{DEPRECATED_UBBLE_PREFIX}{fraud_check.thirdPartyId}"

    pcapi_repository.repository.save(fraud_check, new_fraud_check)

    return new_fraud_check


def get_id_provider_detected_eligibility(
    user: users_models.User, identity_content: common_fraud_models.IdentityCheckContent
) -> users_models.EligibilityType | None:
    return fraud_api.decide_eligibility(
        user, identity_content.get_birth_date(), identity_content.get_registration_datetime()
    )


# TODO (Lixxday): use a proper BeneficiaryFraudCheck History model to track these kind of updates
def handle_eligibility_difference_between_declaration_and_identity_provider(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> fraud_models.BeneficiaryFraudCheck:
    identity_content: common_fraud_models.IdentityCheckContent = fraud_check.source_data()  # type: ignore [assignment]

    declared_eligibility = fraud_check.eligibilityType
    id_provider_detected_eligibility = get_id_provider_detected_eligibility(user, identity_content)

    if declared_eligibility == id_provider_detected_eligibility or id_provider_detected_eligibility is None:
        return fraud_check

    new_fraud_check = _update_fraud_check_eligibility_with_history(fraud_check, id_provider_detected_eligibility)

    # Handle eligibility update for PROFILE_COMPLETION fraud check, if it exists
    profile_completion_fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.user == user,
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.PROFILE_COMPLETION,
        fraud_models.BeneficiaryFraudCheck.eligibilityType == declared_eligibility,
    ).first()
    if profile_completion_fraud_check:
        _update_fraud_check_eligibility_with_history(profile_completion_fraud_check, id_provider_detected_eligibility)

    return new_fraud_check


def update_user_birth_date_if_not_beneficiary(user: users_models.User, birth_date: datetime.date | None) -> None:
    """Updates the user validated birth date based on data received from the identity provider
    so that the user is correctly redirected for the rest of the process.
    """
    if user.is_beneficiary:
        return
    if user.validatedBirthDate != birth_date and birth_date is not None:
        user.dateOfBirth = birth_date  # TODO (PC-17174) stop overriding this field
        user.validatedBirthDate = birth_date
        pcapi_repository.repository.save(user)


def _get_jouve_subscription_item_status(
    user: users_models.User,
    eligibility: users_models.EligibilityType | None,
    jouve_fraud_checks: list[fraud_models.BeneficiaryFraudCheck],
) -> models.SubscriptionItemStatus:
    if any(check.status == fraud_models.FraudCheckStatus.OK for check in jouve_fraud_checks):
        return models.SubscriptionItemStatus.OK
    if any(check.status == fraud_models.FraudCheckStatus.KO for check in jouve_fraud_checks):
        return models.SubscriptionItemStatus.KO
    if any(check.status == fraud_models.FraudCheckStatus.SUSPICIOUS for check in jouve_fraud_checks):
        return models.SubscriptionItemStatus.SUSPICIOUS
    if any(check.status == fraud_models.FraudCheckStatus.PENDING for check in jouve_fraud_checks):
        return models.SubscriptionItemStatus.PENDING

    if is_eligibility_activable(user, eligibility):
        return models.SubscriptionItemStatus.TODO

    return models.SubscriptionItemStatus.VOID


def get_first_registration_date(
    user: users_models.User,
    birth_date: datetime.date | None,
    eligibility: users_models.EligibilityType,
) -> datetime.datetime | None:
    fraud_checks = user.beneficiaryFraudChecks
    if not fraud_checks or not birth_date:
        return None

    registration_dates_when_eligible = [
        fraud_check.get_min_date_between_creation_and_registration()
        for fraud_check in fraud_checks
        if fraud_check.eligibilityType == eligibility
        and users_api.is_user_age_compatible_with_eligibility(
            users_utils.get_age_at_date(birth_date, fraud_check.get_min_date_between_creation_and_registration()),
            eligibility,
        )
    ]

    return min(registration_dates_when_eligible) if registration_dates_when_eligible else None


def get_subscription_message(user: users_models.User) -> models.SubscriptionMessage | None:
    """The subscription message is meant to help the user have information about the subscription status."""
    if not users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility):
        return None

    next_step = get_next_subscription_step(user)

    if next_step is not None and next_step not in [
        models.SubscriptionStep.IDENTITY_CHECK,
        models.SubscriptionStep.MAINTENANCE,
    ]:
        # in this case the user is not supposed to need any information and can proceed with the subscription
        return None

    if next_step == models.SubscriptionStep.MAINTENANCE:
        return subscription_messages.MAINTENANCE_PAGE_MESSAGE

    fraud_checks = sorted(
        [check for check in user.beneficiaryFraudChecks if user.eligibility in check.applicable_eligibilities],
        key=lambda check: check.dateCreated,
        reverse=True,
    )

    dms_check = next(
        (
            check
            for check in fraud_checks
            if check.type == fraud_models.FraudCheckType.DMS and check.status != fraud_models.FraudCheckStatus.CANCELED
        ),
        None,
    )
    if dms_check is not None:
        return dms_subscription_api.get_dms_subscription_message(dms_check)

    ubble_check = next(
        (check for check in fraud_checks if check.type == fraud_models.FraudCheckType.UBBLE),
        None,
    )
    if ubble_check is not None:
        return ubble_subscription_api.get_ubble_subscription_message(ubble_check, is_retryable=next_step is not None)

    educonnect_check = next(
        (check for check in fraud_checks if check.type == fraud_models.FraudCheckType.EDUCONNECT),
        None,
    )
    if educonnect_check is not None:
        return educonnect_subscription_api.get_educonnect_subscription_message(educonnect_check)

    user_profiling_ko_check = next(
        (
            check
            for check in fraud_checks
            if check.type == fraud_models.FraudCheckType.USER_PROFILING
            and check.status == USER_PROFILING_BLOCKING_STATUS
        ),
        None,
    )
    if user_profiling_ko_check is not None:
        return subscription_messages.get_user_profiling_ko_message(user.id)

    return None
