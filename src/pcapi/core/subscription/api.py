import logging
from typing import Optional

from pcapi.core.fraud import exceptions as fraud_exceptions
import pcapi.core.fraud.models as fraud_models
from pcapi.core.payments import api as payments_api
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exception
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.external import update_external_user
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportSources
from pcapi.models import ImportStatus
from pcapi.models import db
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
    details: str,
    status: ImportStatus = ImportStatus.CREATED,
) -> None:
    beneficiary_import = BeneficiaryImport.query.filter_by(
        applicationId=application_id,
        sourceId=source_id,
        source=source.value,
        beneficiary=beneficiary,
    ).one_or_none()
    if not beneficiary_import:
        beneficiary_import = BeneficiaryImport(
            applicationId=application_id,
            sourceId=source_id,
            source=source.value,
            beneficiary=beneficiary,
        )

    beneficiary_import.setStatus(status=status, detail=details)
    beneficiary_import.beneficiary = beneficiary

    pcapi_repository.repository.save(beneficiary_import)


def get_latest_subscription_message(user: users_models.User) -> Optional[models.SubscriptionMessage]:
    return models.SubscriptionMessage.query.filter_by(user=user).order_by(models.SubscriptionMessage.id.desc()).first()


def activate_beneficiary(user: users_models.User, deposit_source: str = None) -> users_models.User:
    if not deposit_source:
        beneficiary_import = subscription_repository.get_beneficiary_import_for_beneficiary(user)
        if not beneficiary_import:
            raise exceptions.BeneficiaryImportMissingException()

        eligibility = beneficiary_import.eligibilityType
        deposit_source = beneficiary_import.get_detailed_source()
    else:
        eligibility = users_models.EligibilityType.AGE18

    if eligibility == users_models.EligibilityType.UNDERAGE:
        user.add_underage_beneficiary_role()
    elif eligibility == users_models.EligibilityType.AGE18:
        user.add_beneficiary_role()
    else:
        raise users_exception.InvalidEligibilityTypeException()

    if "apps_flyer" in user.externalIds:
        apps_flyer_job.log_user_becomes_beneficiary_event_job.delay(user.id)

    deposit = payments_api.create_deposit(user, deposit_source=deposit_source, eligibility=eligibility)

    db.session.add_all((user, deposit))
    db.session.commit()
    update_external_user(user)

    logger.info("Activated beneficiary and created deposit", extra={"user": user.id, "source": deposit_source})
    return user


def check_and_activate_beneficiary(userId: int, deposit_source: str = None) -> users_models.User:
    with pcapi_repository.transaction():
        user = users_repository.get_and_lock_user(userId)
        # TODO: Handle switch from underage_beneficiary to beneficiary
        if user.is_beneficiary or not user.hasCompletedIdCheck:
            db.session.rollback()
            return user
        user = activate_beneficiary(user, deposit_source)
        return user


def create_beneficiary_import(user: users_models.User) -> None:
    if not user.beneficiaryFraudResult:
        raise exceptions.BeneficiaryFraudResultMissing()
    fraud_result: fraud_models.BeneficiaryFraudResult = user.beneficiaryFraudResult
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
        # TODO(viconnex): select the eligibilityType according to the subscription date
        eligibilityType=users_models.EligibilityType.UNDERAGE,
    )
    beneficiary_import.setStatus(ImportStatus.CREATED)
    pcapi_repository.repository.save(beneficiary_import)

    users_api.update_user_information_from_external_source(user, fraud_check.source_data(), commit=True)
