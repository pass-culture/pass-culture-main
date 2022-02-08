import datetime
import logging
import typing

from pcapi import settings
import pcapi.core.fraud.api as fraud_api
from pcapi.core.fraud.common import models as common_fraud_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.repository as fraud_repository
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.mails.transactional.users import accepted_as_beneficiary
from pcapi.core.payments import api as payments_api
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.domain import user_emails as old_user_emails
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.feature import FeatureToggle
import pcapi.repository as pcapi_repository
from pcapi.workers import apps_flyer_job

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


def attach_beneficiary_import_details(
    beneficiary: users_models.User,
    application_id: int,
    source_id: int,
    source: BeneficiaryImportSources,
    eligibility_type: typing.Optional[users_models.EligibilityType],
    details: typing.Optional[str] = None,
    status: ImportStatus = ImportStatus.CREATED,
) -> None:
    beneficiary_import = BeneficiaryImport.query.filter_by(
        applicationId=application_id,
        sourceId=source_id,
        source=source.value,
        beneficiary=beneficiary,
        eligibilityType=eligibility_type,
    ).one_or_none()
    if not beneficiary_import:
        beneficiary_import = BeneficiaryImport(
            applicationId=application_id,
            sourceId=source_id,
            source=source.value,
            beneficiary=beneficiary,
            eligibilityType=eligibility_type,
        )

    beneficiary_import.setStatus(status=status, detail=details)
    beneficiary_import.beneficiary = beneficiary

    pcapi_repository.repository.save(beneficiary_import)


def get_latest_subscription_message(user: users_models.User) -> typing.Optional[models.SubscriptionMessage]:
    return models.SubscriptionMessage.query.filter_by(user=user).order_by(models.SubscriptionMessage.id.desc()).first()


def create_successfull_beneficiary_import(
    user: users_models.User,
    source: BeneficiaryImportSources,
    source_id: typing.Optional[int] = None,
    application_id: typing.Optional[int] = None,
    eligibility_type: typing.Optional[users_models.EligibilityType] = None,
    third_party_id: typing.Optional[str] = None,
) -> None:
    if application_id:
        beneficiary_import_filter = BeneficiaryImport.applicationId == application_id
    elif third_party_id:
        beneficiary_import_filter = BeneficiaryImport.thirdPartyId == third_party_id
    else:
        raise ValueError(
            "create_successfull_beneficiary_import need need a non-None value for application_id or third_party_id"
        )
    existing_beneficiary_import = BeneficiaryImport.query.filter(beneficiary_import_filter).first()

    beneficiary_import = existing_beneficiary_import or BeneficiaryImport()
    if not beneficiary_import.beneficiary:
        beneficiary_import.beneficiary = user
    if eligibility_type is not None:
        beneficiary_import.eligibilityType = eligibility_type

    beneficiary_import.applicationId = application_id
    beneficiary_import.sourceId = source_id
    beneficiary_import.source = source.value
    beneficiary_import.setStatus(status=ImportStatus.CREATED, author=None)
    beneficiary_import.thirdPartyId = third_party_id

    pcapi_repository.repository.save(beneficiary_import)

    return beneficiary_import


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

    user.hasCompletedIdCheck = False

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
    # TODO(add a check on user.activity once the field is mandatory in subscription/profile_completion route)
    return user.city is not None


def needs_to_perform_identity_check(user: users_models.User) -> bool:
    # TODO (viconnex) refacto this method to base result on fraud_checks made
    return (
        not user.hasCompletedIdCheck
        and not (
            not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)
            and FeatureToggle.ENABLE_UBBLE.is_active()
        )
        and not (fraud_api.has_passed_educonnect(user) and user.eligibility == users_models.EligibilityType.UNDERAGE)
    )


def _is_eligibility_activable(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> bool:
    return user.eligibility == eligibility and users_api.is_eligible_for_beneficiary_upgrade(user, eligibility)


def get_email_validation_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    if user.isEmailValidated:
        status = models.SubscriptionItemStatus.OK
    else:
        if _is_eligibility_activable(user, eligibility):
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
            elif _is_eligibility_activable(user, eligibility):
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

        elif _is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.USER_PROFILING, status=status)


def get_profile_completion_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    if has_completed_profile(user):
        status = models.SubscriptionItemStatus.OK
    elif _is_eligibility_activable(user, eligibility):
        status = models.SubscriptionItemStatus.TODO
    else:
        status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PROFILE_COMPLETION, status=status)


def get_identity_check_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    identity_fraud_checks = fraud_repository.get_identity_fraud_checks(user, eligibility)

    if any(check.status == fraud_models.FraudCheckStatus.OK for check in identity_fraud_checks):
        status = models.SubscriptionItemStatus.OK
    elif any(check.status == fraud_models.FraudCheckStatus.PENDING for check in identity_fraud_checks):
        # TODO(consider ubble checks status STARTED as TODO when the status STARTED is introduced)
        status = models.SubscriptionItemStatus.PENDING
    elif any(check.status == fraud_models.FraudCheckStatus.SUSPICIOUS for check in identity_fraud_checks):
        status = models.SubscriptionItemStatus.SUSPICIOUS
    elif any(check.status == fraud_models.FraudCheckStatus.KO for check in identity_fraud_checks):
        status = models.SubscriptionItemStatus.KO
    else:
        if _is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.IDENTITY_CHECK, status=status)


def get_honor_statement_subscription_item(
    user: users_models.User, eligibility: typing.Optional[users_models.EligibilityType]
) -> models.SubscriptionItem:
    if fraud_api.has_performed_honor_statement(user, eligibility):
        status = models.SubscriptionItemStatus.OK
    else:
        if _is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.HONOR_STATEMENT, status=status)


# pylint: disable=too-many-return-statements
def get_next_subscription_step(user: users_models.User) -> typing.Optional[models.SubscriptionStep]:
    # TODO(viconnex): use SubscriptionItems when user.hasCompletedIdCheck is removed and STARTED status is used in ubble workflow
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

    if needs_to_perform_identity_check(user):
        if not get_allowed_identity_check_methods(user):
            return models.SubscriptionStep.MAINTENANCE
        return models.SubscriptionStep.IDENTITY_CHECK

    if not fraud_api.has_performed_honor_statement(user, user.eligibility):
        return models.SubscriptionStep.HONOR_STATEMENT

    return None


def update_user_profile(
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

    users_api.update_external_user(user)

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

    if (
        user.eligibility == users_models.EligibilityType.UNDERAGE
        and FeatureToggle.ENABLE_NATIVE_EAC_INDIVIDUAL.is_active()
    ):
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


def activate_beneficiary_if_no_missing_step(user: users_models.User) -> None:
    if has_passed_all_checks_to_become_beneficiary(user):
        activate_beneficiary(user)  # calls update_external_user
    else:
        users_external.update_external_user(user)


def on_successful_application(
    user: users_models.User,
    source_data: common_fraud_models.IdentityCheckContent,
) -> None:
    users_api.update_user_information_from_external_source(user, source_data)

    # TODO (viconnex) remove when we also look for DMS files to know if the user has completed id check
    user.hasCompletedIdCheck = True

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

    if not fraud_api.has_performed_honor_statement(user, fraud_check.eligibilityType):
        if not FeatureToggle.IS_HONOR_STATEMENT_MANDATORY_TO_ACTIVATE_BENEFICIARY.is_active():
            logger.warning("The honor statement has not been performed or recorded", extra={"user_id": user.id})
        else:
            return False

    return True
