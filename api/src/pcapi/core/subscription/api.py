import logging
from typing import Optional

import flask

from pcapi.connectors.beneficiaries import ubble
from pcapi.core.fraud import exceptions as fraud_exceptions
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.repository as fraud_repository
from pcapi.core.mails.transactional.users import accepted_as_beneficiary_email
from pcapi.core.payments import api as payments_api
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exception
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.domain import user_emails as old_user_emails
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.feature import FeatureToggle
import pcapi.repository as pcapi_repository
from pcapi.repository import transaction
from pcapi.workers import apps_flyer_job

from . import exceptions
from . import models
from . import repository as subscription_repository


logger = logging.getLogger(__name__)


def attach_beneficiary_import_details(
    beneficiary: users_models.User,
    application_id: int,
    source_id: int,
    source: BeneficiaryImportSources,
    eligibility_type: Optional[users_models.EligibilityType],
    details: Optional[str] = None,
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


def get_latest_subscription_message(user: users_models.User) -> Optional[models.SubscriptionMessage]:
    return models.SubscriptionMessage.query.filter_by(user=user).order_by(models.SubscriptionMessage.id.desc()).first()


def create_successfull_beneficiary_import(
    user: users_models.User,
    source: BeneficiaryImportSources,
    source_id: str,
    application_id: str,
    eligibility_type: Optional[users_models.EligibilityType] = None,
) -> None:
    existing_beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=application_id).first()

    beneficiary_import = existing_beneficiary_import or BeneficiaryImport()
    if not beneficiary_import.beneficiary:
        beneficiary_import.beneficiary = user
    if eligibility_type is not None:
        beneficiary_import.eligibilityType = eligibility_type

    beneficiary_import.applicationId = application_id
    beneficiary_import.sourceId = source_id
    beneficiary_import.source = source.value
    beneficiary_import.setStatus(status=ImportStatus.CREATED, author=None)

    pcapi_repository.repository.save(beneficiary_import)

    return beneficiary_import


def activate_beneficiary(
    user: users_models.User, deposit_source: str = None, has_activated_account: Optional[bool] = True
) -> users_models.User:

    beneficiary_import = subscription_repository.get_beneficiary_import_for_beneficiary(user)
    if not beneficiary_import:
        raise exceptions.BeneficiaryImportMissingException()

    eligibility = beneficiary_import.eligibilityType
    deposit_source = beneficiary_import.get_detailed_source()

    if not user.is_eligible_for_beneficiary_upgrade:
        raise exceptions.CannotUpgradeBeneficiaryRole()

    if eligibility == users_models.EligibilityType.UNDERAGE:
        user.add_underage_beneficiary_role()
    elif eligibility == users_models.EligibilityType.AGE18:
        user.add_beneficiary_role()
        user.remove_underage_beneficiary_role()
    else:
        raise users_exception.InvalidEligibilityTypeException()

    if "apps_flyer" in user.externalIds:
        apps_flyer_job.log_user_becomes_beneficiary_event_job.delay(user.id)

    deposit = payments_api.create_deposit(user, deposit_source=deposit_source, eligibility=eligibility)

    user.hasCompletedIdCheck = False

    db.session.add_all((user, deposit))
    db.session.commit()
    logger.info("Activated beneficiary and created deposit", extra={"user": user.id, "source": deposit_source})

    db.session.refresh(user)

    users_external.update_external_user(user)
    _send_beneficiary_activation_email(user, has_activated_account)

    return user


def check_and_activate_beneficiary(
    userId: int, deposit_source: str = None, has_activated_account: Optional[bool] = True
) -> users_models.User:
    with pcapi_repository.transaction():
        user = users_repository.get_and_lock_user(userId)

        if not user.hasCompletedIdCheck:
            db.session.rollback()
            return user
        try:
            user = activate_beneficiary(user, deposit_source, has_activated_account)
        except subscription_exceptions.CannotUpgradeBeneficiaryRole:
            db.session.rollback()
            return user
        return user


def create_beneficiary_import(user: users_models.User, eligibilityType: users_models.EligibilityType) -> None:
    fraud_result = fraud_models.BeneficiaryFraudResult.query.filter_by(
        user=user,
        # find fraud result by eligibility. If eligibilityType is None, the FraudResult has the default value AGE18
        eligibilityType=eligibilityType or users_models.EligibilityType.AGE18,
    ).one_or_none()
    if not fraud_result:
        raise exceptions.BeneficiaryFraudResultMissing()

    fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
        user=user,
        type=fraud_models.FraudCheckType.EDUCONNECT,
    ).one_or_none()

    fraud_ko_reasons = fraud_result.reason_codes
    if fraud_models.FraudReasonCode.DUPLICATE_USER in fraud_ko_reasons:
        raise fraud_exceptions.DuplicateUser()

    if fraud_models.FraudReasonCode.AGE_NOT_VALID in fraud_ko_reasons:
        raise fraud_exceptions.UserAgeNotValid()

    if fraud_models.FraudReasonCode.INE_NOT_WHITELISTED in fraud_ko_reasons:
        raise fraud_exceptions.NotWhitelistedINE()

    if fraud_check.type != fraud_models.FraudCheckType.EDUCONNECT:
        raise NotImplementedError()

    if fraud_result.status != fraud_models.FraudStatus.OK:
        raise fraud_exceptions.FraudException()

    beneficiary_import = BeneficiaryImport(
        thirdPartyId=fraud_check.thirdPartyId,
        beneficiaryId=user.id,
        sourceId=None,
        source=BeneficiaryImportSources.educonnect.value,
        beneficiary=user,
        eligibilityType=eligibilityType,
    )
    beneficiary_import.setStatus(ImportStatus.CREATED)
    pcapi_repository.repository.save(beneficiary_import)

    users_api.update_user_information_from_external_source(user, fraud_check.source_data(), commit=True)


def _send_beneficiary_activation_email(user: users_models.User, has_activated_account: bool):
    if not has_activated_account:
        old_user_emails.send_activation_email(
            user=user, reset_password_token_life_time=users_constants.RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
        )
    else:
        accepted_as_beneficiary_email.send_accepted_as_beneficiary_email(user=user)


def start_ubble_workflow(user: users_models.User, redirect_url: str) -> str:
    content = ubble.start_identification(
        user_id=user.id,
        phone_number=user.phoneNumber,
        birth_date=user.dateOfBirth.date(),
        first_name=user.firstName,
        last_name=user.lastName,
        webhook_url=flask.url_for("Public API.ubble_webhook_update_application_status", _external=True),
        redirect_url=redirect_url,
    )
    fraud_api.start_ubble_fraud_check(user, content)
    return content.identification_url


def update_ubble_workflow(
    fraud_check: fraud_models.BeneficiaryFraudCheck, status: fraud_models.IdentificationStatus
) -> fraud_models.BeneficiaryFraudCheck:
    content = ubble.get_content(fraud_check.thirdPartyId)
    fraud_check.resultContent = content
    pcapi_repository.repository.save(fraud_check)

    user = fraud_check.user

    if status == fraud_models.IdentificationStatus.PROCESSING:
        user.hasCompletedIdCheck = True
        pcapi_repository.repository.save(user)

    elif status == fraud_models.IdentificationStatus.PROCESSED:
        fraud_api.on_ubble_result(fraud_check)

    return fraud_check


# pylint: disable=too-many-return-statements
def get_next_subscription_step(user: users_models.User) -> Optional[models.SubscriptionStep]:
    # TODO(viconnex): base the next step on the user.subscriptionState that will be added later on
    allowed_identity_check_methods = get_allowed_identity_check_methods(user)
    if not allowed_identity_check_methods:
        return models.SubscriptionStep.MAINTENANCE
    if not user.isEmailValidated:
        return models.SubscriptionStep.EMAIL_VALIDATION

    if not user.is_eligible_for_beneficiary_upgrade():
        return None

    if (
        not user.is_phone_validated
        and user.eligibility == users_models.EligibilityType.AGE18
        and FeatureToggle.ENABLE_PHONE_VALIDATION.is_active()
    ):
        return models.SubscriptionStep.PHONE_VALIDATION

    if user.eligibility == users_models.EligibilityType.AGE18:
        user_profiling = fraud_repository.get_last_user_profiling_fraud_check(user)

        if not user_profiling:
            return models.SubscriptionStep.USER_PROFILING

        if user_profiling.source_data().risk_rating == fraud_models.UserProfilingRiskRating.HIGH:
            return None

    if not user.address:
        return models.SubscriptionStep.PROFILE_COMPLETION

    if (
        not user.hasCompletedIdCheck
        and user.allowed_eligibility_check_methods
        and not user.extraData.get("is_identity_document_uploaded")
    ):
        return models.SubscriptionStep.IDENTITY_CHECK

    return None


def update_user_profile(
    user: users_models.User,
    address: Optional[str],
    city: str,
    postal_code: str,
    activity: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    school_type: Optional[users_models.SchoolType] = None,
    phone_number: Optional[str] = None,
) -> None:
    user_initial_roles = user.roles

    update_payload = {
        "address": address,
        "city": city,
        "postalCode": postal_code,
        "departementCode": PostalCode(postal_code).get_departement_code(),
        "activity": activity,
        "hasCompletedIdCheck": True,
        "schoolType": school_type,
    }

    if first_name and not user.firstName:
        update_payload["firstName"] = first_name

    if last_name and not user.lastName:
        update_payload["lastName"] = last_name

    # TODO (viconnex): remove phone number update after app native mandatory version is >= 164
    if not FeatureToggle.ENABLE_PHONE_VALIDATION.is_active() and not user.phoneNumber and phone_number:
        update_payload["phoneNumber"] = phone_number

    with transaction():
        users_models.User.query.filter(users_models.User.id == user.id).update(update_payload)
    db.session.refresh(user)

    if (
        not users_api.steps_to_become_beneficiary(user)
        # the 2 following checks should be useless
        and fraud_api.has_user_performed_identity_check(user)
        and not fraud_api.is_user_fraudster(user)
    ):
        check_and_activate_beneficiary(user.id)
    else:
        users_api.update_external_user(user)

    new_user_roles = user.roles
    underage_user_has_been_activated = (
        users_models.UserRole.UNDERAGE_BENEFICIARY in new_user_roles
        and users_models.UserRole.UNDERAGE_BENEFICIARY not in user_initial_roles
    )

    logger.info(
        "User id check profile updated",
        extra={"user": user.id, "has_been_activated": user.has_beneficiary_role or underage_user_has_been_activated},
    )


def is_identity_check_with_document_method_allowed_for_underage(user: users_models.User) -> bool:

    if not FeatureToggle.ALLOW_IDCHECK_UNDERAGE_REGISTRATION.is_active():
        return False

    if (
        user.schoolType == users_models.SchoolType.PUBLIC_HIGH_SCHOOL
        or user.schoolType == users_models.SchoolType.PUBLIC_SECONDARY_SCHOOL
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
            allowed_methods.append(
                models.IdentityCheckMethod.UBBLE
                if FeatureToggle.ENABLE_UBBLE.is_active()
                else models.IdentityCheckMethod.JOUVE
            )

    elif user.eligibility == users_models.EligibilityType.AGE18:
        if FeatureToggle.ALLOW_IDCHECK_REGISTRATION.is_active():
            allowed_methods.append(
                models.IdentityCheckMethod.UBBLE
                if FeatureToggle.ENABLE_UBBLE.is_active()
                else models.IdentityCheckMethod.JOUVE
            )

    return allowed_methods


def get_maintenance_page_type(user: users_models.User) -> Optional[models.MaintenancePageType]:
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


def on_successful_application(
    user: users_models.User, source_data: fraud_models.DMSContent, application_id: int, source_id: int
):
    users_api.update_user_information_from_external_source(user, source_data)
    # unsure ?
    user.hasCompletedIdCheck = True
    pcapi_repository.repository.save(user)

    create_successfull_beneficiary_import(
        user=user,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=source_id,
        application_id=application_id,
        eligibility_type=fraud_api.get_eligibility_type(source_data),
    )

    if not users_api.steps_to_become_beneficiary(user):
        activate_beneficiary(user)
    else:
        users_external.update_external_user(user)
