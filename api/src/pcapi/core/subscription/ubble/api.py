import logging
import mimetypes
import os
import pathlib
import shutil
import tempfile

import flask
from pydantic.v1.networks import HttpUrl

from pcapi import settings
from pcapi.connectors.beneficiaries import outscale
from pcapi.connectors.beneficiaries import ubble
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.external.batch as batch_notification
from pcapi.core.external.batch import track_ubble_ko_event
from pcapi.core.fraud.exceptions import IncompatibleFraudCheckStatus
import pcapi.core.fraud.models as fraud_models
from pcapi.core.fraud.ubble import api as ubble_fraud_api
import pcapi.core.fraud.ubble.constants as ubble_fraud_constants
import pcapi.core.fraud.ubble.models as ubble_fraud_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.exceptions import BeneficiaryFraudCheckMissingException
from pcapi.core.users import models as users_models
import pcapi.repository as pcapi_repository
from pcapi.tasks import ubble_tasks
from pcapi.utils import requests as requests_utils

from . import exceptions
from . import messages
from . import models


logger = logging.getLogger(__name__)


def update_ubble_workflow(fraud_check: fraud_models.BeneficiaryFraudCheck) -> None:
    content = ubble.get_content(fraud_check.thirdPartyId)
    status = content.status

    if settings.ENABLE_UBBLE_TEST_EMAIL and ubble_fraud_api.does_match_ubble_test_email(fraud_check.user.email):
        content.birth_date = fraud_check.user.birth_date

    fraud_check.resultContent = content
    pcapi_repository.repository.save(fraud_check)

    user: users_models.User = fraud_check.user

    if status == ubble_fraud_models.UbbleIdentificationStatus.PROCESSING:
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
            handle_validation_errors(user, fraud_check)

            return

        payload = ubble_tasks.StoreIdPictureRequest(identification_id=fraud_check.thirdPartyId)
        ubble_tasks.store_id_pictures_task.delay(payload)

        try:
            is_activated = subscription_api.activate_beneficiary_if_no_missing_step(user=user)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failure after ubble successful result", extra={"user_id": user.id})
            return

        if not is_activated:
            external_attributes_api.update_external_user(user)

    elif status in (
        ubble_fraud_models.UbbleIdentificationStatus.ABORTED,
        ubble_fraud_models.UbbleIdentificationStatus.EXPIRED,
    ):
        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        pcapi_repository.repository.save(fraud_check)


def start_ubble_workflow(user: users_models.User, first_name: str, last_name: str, redirect_url: str) -> HttpUrl | None:
    content = ubble.start_identification(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        webhook_url=flask.url_for("Public API.ubble_webhook_update_application_status", _external=True),
        redirect_url=redirect_url,
    )
    fraud_check = subscription_api.initialize_identity_fraud_check(
        eligibility_type=user.eligibility,
        fraud_check_type=fraud_models.FraudCheckType.UBBLE,
        identity_content=content,
        third_party_id=str(content.identification_id),
        user=user,
    )
    batch_notification.track_identity_check_started_event(user.id, fraud_check.type)

    return content.identification_url


def get_most_relevant_ubble_error(
    reason_codes: list[fraud_models.FraudReasonCode],
) -> fraud_models.FraudReasonCode | None:
    return next(
        iter(
            sorted(
                reason_codes,
                key=lambda reason_code: (
                    models.UBBLE_CODE_ERROR_MAPPING[reason_code].priority
                    if reason_code in models.UBBLE_CODE_ERROR_MAPPING
                    else 0
                ),
                reverse=True,
            )
        ),
        None,
    )


def _requires_reminder(error_code: fraud_models.FraudReasonCode | None) -> bool:
    return (
        error_code in ubble_fraud_constants.REASON_CODE_REQUIRING_IMMEDIATE_NOTIFICATION_REMINDER
        or error_code in ubble_fraud_constants.REASON_CODE_REQUIRING_IMMEDIATE_EMAIL_REMINDER
    )


def _dispatch_reminder(user: users_models.User, error_code: fraud_models.FraudReasonCode | None) -> None:
    if error_code in ubble_fraud_constants.REASON_CODE_REQUIRING_IMMEDIATE_EMAIL_REMINDER:
        transactional_mails.send_subscription_document_error_email(user.email, error_code)
    if error_code in ubble_fraud_constants.REASON_CODE_REQUIRING_IMMEDIATE_NOTIFICATION_REMINDER:
        track_ubble_ko_event(user.id, error_code)


def handle_validation_errors(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> None:
    error_codes = fraud_check.reasonCodes or []
    relevant_error_code = get_most_relevant_ubble_error(error_codes)
    if _requires_reminder(relevant_error_code):
        _dispatch_reminder(user, relevant_error_code)
    elif fraud_models.FraudReasonCode.DUPLICATE_USER in error_codes:
        transactional_mails.send_duplicate_beneficiary_email(
            user, fraud_check.source_data(), fraud_models.FraudReasonCode.DUPLICATE_USER
        )
    elif fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in error_codes:
        transactional_mails.send_duplicate_beneficiary_email(
            user, fraud_check.source_data(), fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER
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
        ubble_content = ubble.get_content(fraud_check.thirdPartyId)
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


def get_ubble_subscription_message(
    ubble_fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> subscription_models.SubscriptionMessage | None:
    if ubble_fraud_check.status == fraud_models.FraudCheckStatus.PENDING:
        return messages.get_application_pending_message(ubble_fraud_check.updatedAt)

    if ubble_fraud_check.status in (
        fraud_models.FraudCheckStatus.SUSPICIOUS,
        fraud_models.FraudCheckStatus.KO,
        fraud_models.FraudCheckStatus.ERROR,
    ):
        if subscription_api.can_retry_identity_fraud_check(ubble_fraud_check):
            return messages.get_ubble_retryable_message(
                ubble_fraud_check.reasonCodes or [], ubble_fraud_check.updatedAt
            )
        return messages.get_ubble_not_retryable_message(ubble_fraud_check)

    return None
