import logging
import typing

import flask

from pcapi import settings
from pcapi.connectors.beneficiaries import ubble
from pcapi.core.fraud import exceptions as fraud_exceptions
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.mails.transactional.users import subscription_document_error
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.users import models as users_models
from pcapi.models.beneficiary_import import BeneficiaryImportSources
import pcapi.repository as pcapi_repository


logger = logging.getLogger(__name__)


def update_ubble_workflow(
    fraud_check: fraud_models.BeneficiaryFraudCheck, status: fraud_models.ubble.UbbleIdentificationStatus
) -> None:
    content = ubble.get_content(fraud_check.thirdPartyId)

    if not settings.IS_PROD and fraud_api.ubble.does_match_ubble_test_email(fraud_check.user.email):
        content.birth_date = fraud_check.user.dateOfBirth.date() if fraud_check.user.dateOfBirth else None

    fraud_check.resultContent = content
    pcapi_repository.repository.save(fraud_check)

    user = fraud_check.user

    if status == fraud_models.ubble.UbbleIdentificationStatus.PROCESSING:
        user.hasCompletedIdCheck = True
        pcapi_repository.repository.save(user)
        subscription_messages.on_review_pending(user)

    elif status == fraud_models.ubble.UbbleIdentificationStatus.PROCESSED:
        try:
            fraud_check = subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(
                fraud_check
            )
            fraud_api.ubble.on_ubble_result(fraud_check)

        except fraud_exceptions.BeneficiaryFraudResultCannotBeDowngraded:
            logger.warning(
                "Trying to downgrade a beneficiary that already has been considered OK", extra={"user_id": user.id}
            )

        except Exception:  # pylint: disable=broad-except
            logger.exception("Error on Ubble fraud check result: %s", extra={"user_id": user.id})

        else:
            if fraud_check.status != fraud_models.FraudCheckStatus.OK:
                can_retry = fraud_api.ubble.is_user_allowed_to_perform_ubble_check(user, fraud_check.eligibilityType)
                handle_validation_errors(user, fraud_check.reasonCodes, can_retry=can_retry)
                subscription_api.update_user_birth_date(user, fraud_check.source_data().get_birth_date())
                return

            try:
                subscription_api.on_successful_application(
                    user=user,
                    source=BeneficiaryImportSources.ubble,
                    source_data=fraud_check.source_data(),
                    eligibility_type=fraud_check.source_data().get_eligibility_type(),
                    third_party_id=fraud_check.thirdPartyId,
                    source_id=None,
                )

            except Exception as err:  # pylint: disable=broad-except
                logger.warning(
                    "Could not save application %s, because of error: %s",
                    fraud_check.thirdPartyId,
                    err,
                )
            else:
                logger.info(
                    "Successfully created user for application %s",
                    fraud_check.thirdPartyId,
                )

    elif status == fraud_models.ubble.UbbleIdentificationStatus.ABORTED:
        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        pcapi_repository.repository.save(fraud_check)


def start_ubble_workflow(user: users_models.User, redirect_url: str) -> str:
    content = ubble.start_identification(
        user_id=user.id,
        phone_number=user.phoneNumber,
        first_name=user.firstName,
        last_name=user.lastName,
        webhook_url=flask.url_for("Public API.ubble_webhook_update_application_status", _external=True),
        redirect_url=redirect_url,
    )
    fraud_api.ubble.start_ubble_fraud_check(user, content)
    return content.identification_url


def is_ubble_workflow_restartable(fraud_check: fraud_models.BeneficiaryFraudCheck) -> bool:
    if fraud_check.type != fraud_models.FraudCheckType.UBBLE:
        return False

    ubble_content: fraud_models.ubble_models.UbbleContent = fraud_check.source_data()
    if ubble_content.status == fraud_models.ubble_models.UbbleIdentificationStatus.INITIATED:
        return True
    return False


def handle_validation_errors(
    user: users_models.User,
    reason_codes: typing.Optional[list[fraud_models.FraudReasonCode]],
    can_retry: bool = False,  # when available
):
    reason_codes = reason_codes or []

    if fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in reason_codes:
        if can_retry:
            subscription_messages.on_idcheck_unread_document_with_retry(user)
        else:
            subscription_messages.on_idcheck_unread_document(user)
        subscription_document_error.send_subscription_document_error_email(user.email, "unread-document")

    elif fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH in reason_codes:
        subscription_messages.on_idcheck_document_data_not_matching(user)
        subscription_document_error.send_subscription_document_error_email(user.email, "information-error")

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in reason_codes:
        if can_retry:
            subscription_messages.on_idcheck_document_not_supported_with_retry(user)
        else:
            subscription_messages.on_idcheck_document_not_supported(user)
        subscription_document_error.send_subscription_document_error_email(user.email, "unread-mrz-document")

    elif fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in reason_codes:
        if can_retry:
            subscription_messages.on_idcheck_invalid_document_date_with_retry(user)
        else:
            subscription_messages.on_idcheck_invalid_document_date(user)
        subscription_document_error.send_subscription_document_error_email(user.email, "invalid-document")

    elif fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER in reason_codes:
        subscription_messages.on_idcheck_rejected(user)

    elif fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        subscription_messages.on_duplicate_user(user)

    elif fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes:
        subscription_messages.on_duplicate_user(user)

    elif fraud_models.FraudReasonCode.ALREADY_BENEFICIARY in reason_codes:
        subscription_messages.on_already_beneficiary(user)

    elif fraud_models.FraudReasonCode.AGE_TOO_YOUNG in reason_codes:
        subscription_messages.on_age_too_young(user)

    elif fraud_models.FraudReasonCode.AGE_TOO_OLD in reason_codes:
        subscription_messages.on_age_too_old(user)

    elif fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes:
        subscription_messages.on_not_eligible(user)

    else:
        subscription_messages.on_ubble_journey_cannot_continue(user)
