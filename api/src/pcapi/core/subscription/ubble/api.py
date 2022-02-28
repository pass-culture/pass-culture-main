import logging
import typing

import flask

from pcapi import settings
from pcapi.connectors.beneficiaries import ubble
import pcapi.core.fraud.models as fraud_models
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.fraud.ubble import constants as ubble_constants
import pcapi.core.fraud.ubble.models as ubble_fraud_models
from pcapi.core.mails.transactional.users import subscription_document_error
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
import pcapi.repository as pcapi_repository


logger = logging.getLogger(__name__)


def update_ubble_workflow(
    fraud_check: fraud_models.BeneficiaryFraudCheck, status: ubble_fraud_models.UbbleIdentificationStatus
) -> None:
    content = ubble.get_content(fraud_check.thirdPartyId)

    if not settings.IS_PROD and ubble_fraud_api.does_match_ubble_test_email(fraud_check.user.email):
        content.birth_date = fraud_check.user.dateOfBirth.date() if fraud_check.user.dateOfBirth else None

    fraud_check.resultContent = content
    pcapi_repository.repository.save(fraud_check)

    user = fraud_check.user

    if status == ubble_fraud_models.UbbleIdentificationStatus.PROCESSING:
        subscription_messages.on_review_pending(user)
        fraud_check.status = fraud_models.FraudCheckStatus.PENDING
        pcapi_repository.repository.save(user, fraud_check)

    elif status == ubble_fraud_models.UbbleIdentificationStatus.PROCESSED:
        fraud_check = subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(
            user, fraud_check
        )
        try:
            ubble_fraud_api.on_ubble_result(fraud_check)

        except Exception:  # pylint: disable=broad-except
            logger.exception("Error on Ubble fraud check result: %s", extra={"user_id": user.id})
            return

        if fraud_check.status != fraud_models.FraudCheckStatus.OK:
            can_retry = ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, fraud_check.eligibilityType)
            handle_validation_errors(user, fraud_check.reasonCodes, can_retry=can_retry)
            subscription_api.update_user_birth_date(user, fraud_check.source_data().get_birth_date())
            return

        try:
            subscription_api.on_successful_application(user=user, source_data=fraud_check.source_data())
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failure after ubble successful result", extra={"user_id"})

    elif status in (
        ubble_fraud_models.UbbleIdentificationStatus.ABORTED,
        ubble_fraud_models.UbbleIdentificationStatus.EXPIRED,
    ):
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
    ubble_fraud_api.start_ubble_fraud_check(user, content)
    return content.identification_url


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


def get_ubble_subscription_item_status(  # pylint: disable=too-many-return-statements
    user: users_models.User,
    eligibility: typing.Optional[users_models.EligibilityType],
    ubble_fraud_checks: list[fraud_models.BeneficiaryFraudCheck],
) -> subscription_models.SubscriptionItemStatus:
    """
    Look for Ubble identifications already filled (the user finished Ubble funnel and we were notified by Ubble).
    The Ubble status is considered, by order of priority:
     - OK if any status is OK
     - KO if any status is KO and its reason is not among the restartable reasons
     - SUSPICIOUS if any status is SUSPICIOUS and its reason is not among the restartable reasons
     - PENDING if any status is PENDING
     - KO if the user has performed more than MAX_UBBLE_RETRIES
     - TODO if the user is eligible for a beneficiary upgrade
     - VOID otherwise
    """
    filled_ubble_checks = [
        check
        for check in ubble_fraud_checks
        if check.status not in (fraud_models.FraudCheckStatus.CANCELED, fraud_models.FraudCheckStatus.STARTED)
    ]

    if any(check.status == fraud_models.FraudCheckStatus.OK for check in filled_ubble_checks):
        return subscription_models.SubscriptionItemStatus.OK

    if any(
        check.status == fraud_models.FraudCheckStatus.KO and not _is_retryable_check(check)
        for check in filled_ubble_checks
    ):
        return subscription_models.SubscriptionItemStatus.KO

    if any(
        check.status == fraud_models.FraudCheckStatus.SUSPICIOUS and not _is_retryable_check(check)
        for check in filled_ubble_checks
    ):
        return subscription_models.SubscriptionItemStatus.SUSPICIOUS

    if any(check.status == fraud_models.FraudCheckStatus.PENDING for check in filled_ubble_checks):
        return subscription_models.SubscriptionItemStatus.PENDING

    if len(filled_ubble_checks) >= ubble_constants.MAX_UBBLE_RETRIES:
        return subscription_models.SubscriptionItemStatus.KO

    if subscription_api.is_eligibility_activable(user, eligibility):
        return subscription_models.SubscriptionItemStatus.TODO

    return subscription_models.SubscriptionItemStatus.VOID


def _is_retryable_check(ubble_check: fraud_models.BeneficiaryFraudCheck) -> bool:
    return ubble_check.reasonCodes and all(
        code in ubble_constants.RESTARTABLE_FRAUD_CHECK_REASON_CODES for code in ubble_check.reasonCodes
    )
