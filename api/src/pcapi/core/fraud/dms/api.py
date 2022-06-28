import logging
import typing
from typing import Optional

from pcapi import settings
from pcapi.connectors.dms.api import DMSGraphQLClient
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription.dms import models as dms_models
import pcapi.core.users.models as users_models
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def get_fraud_check(user: users_models.User, application_number: int) -> Optional[fraud_models.BeneficiaryFraudCheck]:
    return (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.user == user,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.thirdPartyId == str(application_number),
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
        .first()
    )


def create_fraud_check(
    user: users_models.User,
    application_number: int,
    source_data: typing.Optional[fraud_models.DMSContent],
) -> fraud_models.BeneficiaryFraudCheck:
    eligibility_type = (
        fraud_api.decide_eligibility(user, source_data.get_birth_date(), source_data.get_registration_datetime())
        if source_data
        else None
    )
    fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        type=fraud_models.FraudCheckType.DMS,
        thirdPartyId=str(application_number),
        resultContent=source_data.dict() if source_data else None,
        status=fraud_models.FraudCheckStatus.STARTED,
        eligibilityType=eligibility_type,
    )
    repository.save(fraud_check)
    return fraud_check


def get_or_create_fraud_check(
    user: users_models.User, application_number: int, result_content: typing.Optional[fraud_models.DMSContent] = None
) -> fraud_models.BeneficiaryFraudCheck:
    fraud_check = get_fraud_check(user, application_number)
    if fraud_check is None:
        return create_fraud_check(user, application_number, result_content)
    return fraud_check


def on_dms_eligibility_error(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    application_scalar_id: str,
    extra_data: Optional[dict] = None,
) -> None:
    dms_client = DMSGraphQLClient()
    logger.info(
        "Birthdate of DMS application %d shows that user is not eligible",
        fraud_check.thirdPartyId,
        extra=extra_data,
    )
    fraud_check_content = typing.cast(fraud_models.DMSContent, fraud_check.source_data())
    birth_date = fraud_check_content.get_birth_date()
    birth_date_field_error = dms_models.DmsFieldErrorDetails(
        key=dms_models.DmsFieldErrorKeyEnum.birth_date, value=birth_date.isoformat() if birth_date else None
    )
    subscription_messages.on_dms_application_field_errors(
        user,
        [birth_date_field_error],
        is_application_updatable=True,
    )
    dms_client.send_user_message(
        application_scalar_id,
        settings.DMS_INSTRUCTOR_ID,
        subscription_messages.build_field_errors_user_message([birth_date_field_error]),
    )
    fraud_check.reason = "La date de naissance de l'utilisateur ne correspond pas à un âge autorisé"
    fraud_check.reasonCodes = [fraud_models.FraudReasonCode.AGE_NOT_VALID]  # type: ignore [list-item]
    fraud_check.status = fraud_models.FraudCheckStatus.ERROR  # type: ignore [assignment]
    repository.save(fraud_check)
