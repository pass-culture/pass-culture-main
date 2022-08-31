import logging
import mimetypes
import os
import pathlib
import shutil
import tempfile

import flask
from pydantic.networks import HttpUrl

from pcapi import settings
from pcapi.connectors.beneficiaries import outscale
from pcapi.connectors.beneficiaries import ubble
from pcapi.core.fraud.exceptions import IncompatibleFraudCheckStatus
import pcapi.core.fraud.models as fraud_models
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.fraud.ubble import constants as ubble_constants
import pcapi.core.fraud.ubble.models as ubble_fraud_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.exceptions import BeneficiaryFraudCheckMissingException
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
import pcapi.repository as pcapi_repository
from pcapi.tasks import ubble_tasks
from pcapi.utils import requests as requests_utils

from . import exceptions


logger = logging.getLogger(__name__)


def update_ubble_workflow(fraud_check: fraud_models.BeneficiaryFraudCheck) -> None:
    content = ubble.get_content(fraud_check.thirdPartyId)  # type: ignore [arg-type]
    status = content.status

    if not settings.IS_PROD and ubble_fraud_api.does_match_ubble_test_email(fraud_check.user.email):
        content.birth_date = fraud_check.user.dateOfBirth.date() if fraud_check.user.dateOfBirth else None

    fraud_check.resultContent = content  # type: ignore [call-overload]
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

        subscription_api.update_user_birth_date_if_not_beneficiary(user, content.get_birth_date())

        if fraud_check.status != fraud_models.FraudCheckStatus.OK:
            can_retry = ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, fraud_check.eligibilityType)
            handle_validation_errors(user, fraud_check, can_retry=can_retry)
            return

        payload = ubble_tasks.StoreIdPictureRequest(identification_id=fraud_check.thirdPartyId)
        ubble_tasks.store_id_pictures_task.delay(payload)

        try:
            is_activated = subscription_api.activate_beneficiary_if_no_missing_step(user=user)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failure after ubble successful result", extra={"user_id": user.id})

        if not is_activated:
            users_external.update_external_user(user)

    elif status in (
        ubble_fraud_models.UbbleIdentificationStatus.ABORTED,
        ubble_fraud_models.UbbleIdentificationStatus.EXPIRED,
    ):
        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        pcapi_repository.repository.save(fraud_check)


def start_ubble_workflow(user: users_models.User, redirect_url: str) -> str:
    content = ubble.start_identification(
        user_id=user.id,
        first_name=user.firstName,  # type: ignore [arg-type]
        last_name=user.lastName,  # type: ignore [arg-type]
        webhook_url=flask.url_for("Public API.ubble_webhook_update_application_status", _external=True),
        redirect_url=redirect_url,
    )
    ubble_fraud_api.start_ubble_fraud_check(user, content)
    return content.identification_url  # type: ignore [return-value]


def handle_validation_errors(  # type: ignore [no-untyped-def]
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    can_retry: bool = False,  # when available
):
    reason_codes = fraud_check.reasonCodes or []

    if fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in reason_codes:
        if can_retry:
            subscription_messages.on_idcheck_unread_document_with_retry(user)
        else:
            subscription_messages.on_idcheck_unread_document(user)
        transactional_mails.send_subscription_document_error_email(user.email, "unread-document")

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in reason_codes:
        if can_retry:
            subscription_messages.on_idcheck_not_authentic_document_with_retry(user)
        else:
            subscription_messages.on_idcheck_not_authentic_document(user)

    elif fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH in reason_codes:
        subscription_messages.on_idcheck_document_data_not_matching(user)
        transactional_mails.send_subscription_document_error_email(user.email, "information-error")

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in reason_codes:
        if can_retry:
            subscription_messages.on_idcheck_document_not_supported_with_retry(user)
        else:
            subscription_messages.on_idcheck_document_not_supported(user)
        transactional_mails.send_subscription_document_error_email(user.email, "unread-mrz-document")

    elif fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in reason_codes:
        if can_retry:
            subscription_messages.on_idcheck_invalid_document_date_with_retry(user)
        else:
            subscription_messages.on_idcheck_invalid_document_date(user)
        transactional_mails.send_subscription_document_error_email(user.email, "invalid-document")

    elif fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER in reason_codes:
        subscription_messages.on_idcheck_rejected(user)

    elif fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        subscription_messages.on_duplicate_user(user)
        transactional_mails.send_duplicate_beneficiary_email(user, fraud_check.source_data())  # type: ignore [arg-type]

    elif fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes:
        subscription_messages.on_duplicate_user(user)
        transactional_mails.send_duplicate_beneficiary_email(
            user, fraud_check.source_data(), is_id_piece_number_duplicate=True  # type: ignore [arg-type]
        )

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


def get_ubble_subscription_item_status(
    user: users_models.User,
    eligibility: users_models.EligibilityType | None,
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
    return ubble_check.reasonCodes and all(  # type: ignore [return-value]
        code in ubble_constants.RESTARTABLE_FRAUD_CHECK_REASON_CODES for code in ubble_check.reasonCodes
    )


def archive_ubble_user_id_pictures(identification_id: str) -> None:
    # get urls from Ubble
    fraud_check = ubble_fraud_api.get_ubble_fraud_check(identification_id)
    if not fraud_check:
        raise BeneficiaryFraudCheckMissingException(
            f"No validated Identity fraudCheck found with identification_id {identification_id}"
        )

    if fraud_check.status is not fraud_models.FraudCheckStatus.OK:
        raise IncompatibleFraudCheckStatus(
            f"Fraud check status {fraud_check.status} is incompatible with pictures archives for identification_id {identification_id}"
        )

    try:
        ubble_content = ubble.get_content(fraud_check.thirdPartyId)  # type: ignore [arg-type]
    except requests_utils.ExternalAPIException:
        fraud_check.idPicturesStored = False
        pcapi_repository.repository.save(fraud_check)
        raise

    exception_during_process = None
    if ubble_content.signed_image_front_url:
        try:
            _download_and_store_ubble_picture(fraud_check, ubble_content.signed_image_front_url, "front")
        except (exceptions.UbbleDownloadedFileEmpty, requests_utils.ExternalAPIException) as exception:
            exception_during_process = exception
    if ubble_content.signed_image_back_url:
        try:
            _download_and_store_ubble_picture(fraud_check, ubble_content.signed_image_back_url, "back")
        except (exceptions.UbbleDownloadedFileEmpty, requests_utils.ExternalAPIException) as exception:
            exception_during_process = exception

    if exception_during_process:
        fraud_check.idPicturesStored = False
        pcapi_repository.repository.save(fraud_check)
        raise exception_during_process

    fraud_check.idPicturesStored = True
    pcapi_repository.repository.save(fraud_check)


def _download_and_store_ubble_picture(
    fraud_check: fraud_models.BeneficiaryFraudCheck, http_url: HttpUrl, face_name: str
) -> None:
    content_type, raw_file = ubble.download_ubble_picture(http_url)

    file_name = _generate_storable_picture_filename(fraud_check, face_name, content_type)
    file_path = pathlib.Path(tempfile.mkdtemp()) / file_name

    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(raw_file, out_file)

    if os.path.getsize(file_path) == 0:
        logger.error(
            "Ubble picture-download: downloaded file is empty",
            extra={"url": str(http_url)},
        )
        os.remove(file_path)
        raise exceptions.UbbleDownloadedFileEmpty()

    outscale.upload_file(str(fraud_check.userId), str(file_path), str(file_name))
    os.remove(file_path)


def _generate_storable_picture_filename(
    fraud_check: fraud_models.BeneficiaryFraudCheck, face_name: str, mime_type: str | None
) -> str:
    if mime_type is None:
        mime_type = "image/png"  # ubble default picture type is png
    extension = mimetypes.guess_extension(mime_type, strict=True)
    return f"{fraud_check.userId}-{fraud_check.thirdPartyId}-{face_name}{extension}"
