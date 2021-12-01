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
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.feature import FeatureToggle
import pcapi.repository as pcapi_repository
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
    details: Optional[str] = None,
    status: ImportStatus = ImportStatus.CREATED,
    eligibilityType: users_models.EligibilityType = users_models.EligibilityType.AGE18,
) -> None:
    beneficiary_import = BeneficiaryImport.query.filter_by(
        applicationId=application_id,
        sourceId=source_id,
        source=source.value,
        beneficiary=beneficiary,
        eligibilityType=eligibilityType,
    ).one_or_none()
    if not beneficiary_import:
        beneficiary_import = BeneficiaryImport(
            applicationId=application_id,
            sourceId=source_id,
            source=source.value,
            beneficiary=beneficiary,
            eligibilityType=eligibilityType,
        )

    beneficiary_import.setStatus(status=status, detail=details)
    beneficiary_import.beneficiary = beneficiary

    pcapi_repository.repository.save(beneficiary_import)


def get_latest_subscription_message(user: users_models.User) -> Optional[models.SubscriptionMessage]:
    return models.SubscriptionMessage.query.filter_by(user=user).order_by(models.SubscriptionMessage.id.desc()).first()


def create_successfull_beneficiary_import(
    user: users_models.User, source: BeneficiaryImportSources, source_id: str, application_id: str
) -> None:
    existing_beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=application_id).first()

    beneficiary_import = existing_beneficiary_import or BeneficiaryImport()
    if not beneficiary_import.beneficiary:
        beneficiary_import.beneficiary = user

    beneficiary_import.applicationId = application_id
    beneficiary_import.sourceId = source_id
    beneficiary_import.source = source.value
    beneficiary_import.setStatus(status=ImportStatus.CREATED, author=None)

    pcapi_repository.repository.save(beneficiary_import)

    return beneficiary_import


def activate_beneficiary(
    user: users_models.User, deposit_source: str = None, has_activated_account: Optional[bool] = True
) -> users_models.User:
    if not deposit_source:
        beneficiary_import = subscription_repository.get_beneficiary_import_for_beneficiary(user)
        if not beneficiary_import:
            raise exceptions.BeneficiaryImportMissingException()

        eligibility = beneficiary_import.eligibilityType
        deposit_source = beneficiary_import.get_detailed_source()
    else:
        eligibility = users_models.EligibilityType.AGE18

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
        user=user, eligibilityType=eligibilityType
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
    response = ubble.start_identification(
        user_id=user.id,
        phone_number=user.phoneNumber,
        birth_date=user.dateOfBirth.date(),
        first_name=user.firstName,
        last_name=user.lastName,
        webhook_url=flask.url_for("Public API.ubble_webhook_update_application_status", _external=True),
        redirect_url=redirect_url,
        face_required=True,  # TODO(bcalvez): setting ? hardcode ?
    )
    fraud_api.start_ubble_fraud_check(user, response)
    return response.identification_url


# pylint: disable=too-many-return-statements
def get_next_subscription_step(user: users_models.User) -> Optional[models.SubscriptionStep]:
    # TODO(viconnex): base the next step on the user.subscriptionState that will be added later on
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
    )

    if not users_api.steps_to_become_beneficiary(user):
        activate_beneficiary(user)
    else:
        users_external.update_external_user(user)
