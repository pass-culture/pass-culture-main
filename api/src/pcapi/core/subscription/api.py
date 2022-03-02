import datetime
import logging
import typing

from pcapi import settings
import pcapi.core.fraud.api as fraud_api
from pcapi.core.fraud.common import models as common_fraud_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.repository as fraud_repository
from pcapi.core.mails.transactional.users import accepted_as_beneficiary
from pcapi.core.payments import api as payments_api
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.domain import user_emails as old_user_emails
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
import pcapi.repository as pcapi_repository
from pcapi.workers import apps_flyer_job

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


def get_latest_subscription_message(user: users_models.User) -> typing.Optional[models.SubscriptionMessage]:
    return models.SubscriptionMessage.query.filter_by(user=user).order_by(models.SubscriptionMessage.id.desc()).first()


def activate_beneficiary(
    user: users_models.User, deposit_source: str = None, has_activated_account: typing.Optional[bool] = True
) -> users_models.User:
    fraud_check = users_api.get_activable_identity_fraud_check(user)
    if not fraud_check:
        raise exceptions.BeneficiaryFraudCheckMissingException(
            f"No validated Identity fraudCheck found when trying to activate user {user.id}"
        )
    eligibility = fraud_check.eligibilityType
    deposit_source = fraud_check.get_detailed_source()

    if not users_api.is_eligible_for_beneficiary_upgrade(user, eligibility):
        raise exceptions.CannotUpgradeBeneficiaryRole()

    if eligibility == users_models.EligibilityType.UNDERAGE:
        user.validate_user_identity_15_17()
        user.add_underage_beneficiary_role()
    elif eligibility == users_models.EligibilityType.AGE18:
        user.validate_user_identity_18()
        user.add_beneficiary_role()
        user.remove_underage_beneficiary_role()
    else:
        raise exceptions.InvalidEligibilityTypeException()

    if "apps_flyer" in user.externalIds:
        apps_flyer_job.log_user_becomes_beneficiary_event_job.delay(user.id)

    deposit = payments_api.create_deposit(
        user,
        deposit_source=deposit_source,
        eligibility=eligibility,
        age_at_registration=users_utils.get_age_at_date(
            user.dateOfBirth, fraud_check.source_data().get_registration_datetime()
        ),
    )

    db.session.add_all((user, deposit))
    db.session.commit()
    logger.info("Activated beneficiary and created deposit", extra={"user": user.id, "source": deposit_source})

    db.session.refresh(user)

    users_external.update_external_user(user)
    _send_beneficiary_activation_email(user, has_activated_account)

    return user


def _send_beneficiary_activation_email(user: users_models.User, has_activated_account: bool):
    if not has_activated_account:
        old_user_emails.send_activation_email(
            user=user, reset_password_token_life_time=users_constants.RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
        )
    else:
        accepted_as_beneficiary.send_accepted_as_beneficiary_email(user=user)


def has_completed_profile(user: users_models.User) -> bool:
    mandatory_fields = [user.city, user.activity, user.firstName, user.lastName]
    return all(elem is not None for elem in mandatory_fields)


def is_eligibility_activable(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> bool:
    return user.eligibility == eligibility and users_api.is_eligible_for_beneficiary_upgrade(user, eligibility)


def get_email_validation_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
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
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    if eligibility != users_models.EligibilityType.AGE18:
        status = models.SubscriptionItemStatus.NOT_APPLICABLE
    else:
        if user.is_phone_validated:
            status = models.SubscriptionItemStatus.OK
        else:
            if fraud_repository.has_failed_phone_validation(user):
                status = models.SubscriptionItemStatus.KO
            elif not FeatureToggle.ENABLE_PHONE_VALIDATION.is_active():
                status = models.SubscriptionItemStatus.NOT_ENABLED
            elif is_eligibility_activable(user, eligibility):
                status = models.SubscriptionItemStatus.TODO
            else:
                status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PHONE_VALIDATION, status=status)


def get_user_profiling_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    if eligibility != users_models.EligibilityType.AGE18:
        status = models.SubscriptionItemStatus.NOT_APPLICABLE
    else:
        user_profiling = fraud_repository.get_last_user_profiling_fraud_check(user)
        if user_profiling:
            if user_profiling.status == fraud_models.FraudCheckStatus.OK:
                status = models.SubscriptionItemStatus.OK
            elif user_profiling.status == fraud_models.FraudCheckStatus.KO:
                status = models.SubscriptionItemStatus.KO
            elif user_profiling.status == fraud_models.FraudCheckStatus.SUSPICIOUS:
                status = models.SubscriptionItemStatus.SUSPICIOUS
            else:
                logger.exception("Unexpected UserProfiling status %s", user_profiling.status)
                status = models.SubscriptionItemStatus.KO

        elif is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.USER_PROFILING, status=status)


def get_profile_completion_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    if has_completed_profile(user):
        status = models.SubscriptionItemStatus.OK
    elif is_eligibility_activable(user, eligibility):
        status = models.SubscriptionItemStatus.TODO
    else:
        status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PROFILE_COMPLETION, status=status)


def get_identity_check_subscription_status(  # pylint: disable=too-many-return-statements
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    """
    eligibility may be the current user.eligibility or a specific eligibility.
    The result relies on the FraudChecks made with the 3 current identity providers (DMS, Ubble and Educonnect)
    and with the legacy provider (Jouve)
    """
    if eligibility is None:
        return models.SubscriptionItemStatus.VOID

    identity_fraud_checks = fraud_repository.get_identity_fraud_checks(user, eligibility)

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
        return models.SubscriptionItemStatus.OK
    if any(status == models.SubscriptionItemStatus.PENDING for status in statuses):
        return models.SubscriptionItemStatus.PENDING
    if any(status == models.SubscriptionItemStatus.KO for status in statuses):
        return models.SubscriptionItemStatus.KO
    if any(status == models.SubscriptionItemStatus.SUSPICIOUS for status in statuses):
        return models.SubscriptionItemStatus.SUSPICIOUS
    if any(status == models.SubscriptionItemStatus.TODO for status in statuses):
        return models.SubscriptionItemStatus.TODO

    return models.SubscriptionItemStatus.VOID


def get_identity_check_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    status = get_identity_check_subscription_status(user, eligibility)
    return models.SubscriptionItem(type=models.SubscriptionStep.IDENTITY_CHECK, status=status)


def get_honor_statement_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    if fraud_api.has_performed_honor_statement(user, eligibility):
        status = models.SubscriptionItemStatus.OK
    else:
        if is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.HONOR_STATEMENT, status=status)


# pylint: disable=too-many-return-statements
def get_next_subscription_step(user: users_models.User) -> typing.Optional[models.SubscriptionStep]:
    if not user.isEmailValidated:
        return models.SubscriptionStep.EMAIL_VALIDATION

    if not users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility):
        return None

    if user.eligibility == users_models.EligibilityType.AGE18:
        if not user.is_phone_validated and FeatureToggle.ENABLE_PHONE_VALIDATION.is_active():
            return models.SubscriptionStep.PHONE_VALIDATION

        user_profiling = fraud_repository.get_last_user_profiling_fraud_check(user)

        if not user_profiling:
            return models.SubscriptionStep.USER_PROFILING

        if fraud_api.is_risky_user_profile(user):
            return None

    if not has_completed_profile(user):
        return models.SubscriptionStep.PROFILE_COMPLETION

    if _needs_to_perform_identity_check(user):
        if not get_allowed_identity_check_methods(user):
            return models.SubscriptionStep.MAINTENANCE
        return models.SubscriptionStep.IDENTITY_CHECK

    if not fraud_api.has_performed_honor_statement(user, user.eligibility):
        return models.SubscriptionStep.HONOR_STATEMENT

    return None


def _needs_to_perform_identity_check(user) -> bool:
    return get_identity_check_subscription_status(user, user.eligibility) == models.SubscriptionItemStatus.TODO


def complete_profile(
    user: users_models.User,
    address: typing.Optional[str],
    city: str,
    postal_code: str,
    activity: str,
    first_name: typing.Optional[str] = None,
    last_name: typing.Optional[str] = None,
    school_type: typing.Optional[users_models.SchoolTypeEnum] = None,
) -> None:
    update_payload = {
        "address": address,
        "city": city,
        "postalCode": postal_code,
        "departementCode": PostalCode(postal_code).get_departement_code(),
        "activity": activity,
        "schoolType": school_type,
    }

    if first_name and not user.firstName:
        update_payload["firstName"] = first_name

    if last_name and not user.lastName:
        update_payload["lastName"] = last_name

    with pcapi_repository.transaction():
        users_models.User.query.filter(users_models.User.id == user.id).update(update_payload)

    activate_beneficiary_if_no_missing_step(user)

    logger.info("User completed profile step", extra={"user": user.id})


def is_identity_check_with_document_method_allowed_for_underage(user: users_models.User) -> bool:

    if not FeatureToggle.ALLOW_IDCHECK_UNDERAGE_REGISTRATION.is_active():
        return False

    if (
        user.schoolType == users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL
        or user.schoolType == users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL
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


def _is_ubble_allowed_if_subscription_overflow(user: users_models.User) -> bool:
    if not FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION.is_active():
        return True

    future_age = users_utils.get_age_at_date(
        user.dateOfBirth,
        datetime.datetime.utcnow() + datetime.timedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS),
    )
    eligbility_ranges = users_constants.ELIGIBILITY_UNDERAGE_RANGE + [users_constants.ELIGIBILITY_AGE_18]
    eligbility_ranges = [age + 1 for age in eligbility_ranges]
    if future_age > user.age and future_age in eligbility_ranges:
        return True

    return False


def get_maintenance_page_type(user: users_models.User) -> typing.Optional[models.MaintenancePageType]:
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


def activate_beneficiary_if_no_missing_step(user: users_models.User, always_update_attributes=True) -> None:
    if has_passed_all_checks_to_become_beneficiary(user):
        activate_beneficiary(user)  # calls update_external_user
    elif always_update_attributes:
        users_external.update_external_user(user)


def on_successful_application(
    user: users_models.User,
    source_data: common_fraud_models.IdentityCheckContent,
) -> None:
    users_api.update_user_information_from_external_source(user, source_data)

    pcapi_repository.repository.save(user)

    activate_beneficiary_if_no_missing_step(user)


# TODO (Lixxday): use a proper BeneficiaryFraudCHeck History model to track these kind of updates
def handle_eligibility_difference_between_declaration_and_identity_provider(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> fraud_models.BeneficiaryFraudCheck:
    declared_eligibility = fraud_check.eligibilityType
    id_provider_detected_eligibility = fraud_api.decide_eligibility(user, fraud_check.source_data())

    if declared_eligibility == id_provider_detected_eligibility or id_provider_detected_eligibility is None:
        return fraud_check

    # Update fraud check by creating a new one with the correct eligibility
    new_fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=fraud_check.user,
        type=fraud_check.type,
        thirdPartyId=fraud_check.thirdPartyId,
        resultContent=fraud_check.resultContent,
        status=fraud_check.status,
        reason=fraud_check.reason,
        reasonCodes=fraud_check.reasonCodes,
        eligibilityType=id_provider_detected_eligibility,
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
    fraud_check.thirdPartyId = f"deprecated-{fraud_check.thirdPartyId}"

    pcapi_repository.repository.save(new_fraud_check, fraud_check)

    return new_fraud_check


def update_user_birth_date(user: users_models.User, birth_date: typing.Optional[datetime.date]) -> None:
    """Updates the user birth date based on data received from the identity provider.

    Args:
        user (users_models.User): The user to update.
        birth_date (typing.Optional[datetime.date]): The birth date to set.
    """
    if user.is_beneficiary:
        return
    if user.dateOfBirth != birth_date and birth_date is not None:
        user.dateOfBirth = birth_date
        pcapi_repository.repository.save(user)


def has_passed_all_checks_to_become_beneficiary(user: users_models.User) -> bool:
    fraud_check = users_api.get_activable_identity_fraud_check(user)
    if not fraud_check:
        return False

    if (
        not user.is_phone_validated
        and fraud_check.eligibilityType != users_models.EligibilityType.UNDERAGE
        and FeatureToggle.FORCE_PHONE_VALIDATION.is_active()
    ):
        return False

    subscription_item = get_user_profiling_subscription_item(user, fraud_check.eligibilityType)
    if subscription_item.status in (models.SubscriptionItemStatus.TODO, models.SubscriptionItemStatus.KO):
        return False

    profile_completion = get_profile_completion_subscription_item(user, fraud_check.eligibilityType)
    if profile_completion.status != models.SubscriptionItemStatus.OK:
        return False

    if not fraud_api.has_performed_honor_statement(user, fraud_check.eligibilityType):
        return False

    return True


def _get_jouve_subscription_item_status(
    user: users_models.User,
    eligibility: typing.Optional[users_models.EligibilityType],
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
