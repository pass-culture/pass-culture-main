import datetime
import logging
import mimetypes
import os
import pathlib
import re
import shutil
import tempfile
import typing

import flask
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from pydantic.v1.networks import HttpUrl

import pcapi.core.external.batch as batch_notification
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.ubble.constants as ubble_fraud_constants
import pcapi.core.mails.transactional as transactional_mails
import pcapi.utils.repository as pcapi_repository
from pcapi.connectors.beneficiaries import outscale
from pcapi.connectors.beneficiaries import ubble
from pcapi.connectors.serialization import ubble_serializers
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.external.batch import track_ubble_ko_event
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud.exceptions import IncompatibleFraudCheckStatus
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.exceptions import BeneficiaryFraudCheckMissingException
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.tasks import ubble_tasks
from pcapi.utils import requests as requests_utils

from . import errors
from . import exceptions
from . import messages


logger = logging.getLogger(__name__)
PAGE_SIZE = 20_000


def update_ubble_workflow(fraud_check: fraud_models.BeneficiaryFraudCheck) -> None:
    content = _get_content(fraud_check.thirdPartyId)
    _fill_missing_content_test_fields(content, fraud_check)

    _update_identity_fraud_check(fraud_check, content)

    user = fraud_check.user
    status = content.status
    if status in (
        ubble_serializers.UbbleIdentificationStatus.PROCESSING,
        ubble_serializers.UbbleIdentificationStatus.CHECKS_IN_PROGRESS,
    ):
        fraud_check.status = fraud_models.FraudCheckStatus.PENDING
        pcapi_repository.save(user, fraud_check)

    elif status in [
        ubble_serializers.UbbleIdentificationStatus.APPROVED,
        ubble_serializers.UbbleIdentificationStatus.RETRY_REQUIRED,
        ubble_serializers.UbbleIdentificationStatus.DECLINED,
        ubble_serializers.UbbleIdentificationStatus.PROCESSED,
    ]:
        fraud_check = subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(
            user, fraud_check, content
        )
        try:
            ubble_fraud_api.on_ubble_result(fraud_check)
        except Exception:
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
        except Exception:
            logger.exception("Failure after ubble successful result", extra={"user_id": user.id})
            return

        if not is_activated:
            external_attributes_api.update_external_user(user)

    elif status in (
        ubble_serializers.UbbleIdentificationStatus.INCONCLUSIVE,
        ubble_serializers.UbbleIdentificationStatus.REFUSED,
        ubble_serializers.UbbleIdentificationStatus.ABORTED,
        ubble_serializers.UbbleIdentificationStatus.EXPIRED,
    ):
        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        pcapi_repository.save(fraud_check)


def _fill_missing_content_test_fields(
    content: fraud_models.UbbleContent, fraud_check: fraud_models.BeneficiaryFraudCheck
) -> None:
    previous_ubble_content = fraud_check.source_data()
    assert isinstance(previous_ubble_content, fraud_models.UbbleContent)

    user = fraud_check.user
    is_test_identification = (
        ubble_fraud_api.does_match_ubble_test_names(content) or previous_ubble_content.external_applicant_id is not None
    )
    should_fill_content = (
        is_test_identification and content.status == ubble_serializers.UbbleIdentificationStatus.APPROVED
    )
    if should_fill_content:
        content.birth_date = previous_ubble_content.birth_date
        content.id_document_number = previous_ubble_content.id_document_number
        content.first_name = user.firstName
        content.last_name = user.lastName

    if ubble_fraud_api.does_match_ubble_test_email(user.email):
        content.birth_date = user.birth_date


def is_v2_identification(identification_id: str | None) -> bool:
    if not identification_id:
        return True

    V2_IDENTIFICATION_RE = r"^idv_\w+"
    v2_match = re.match(V2_IDENTIFICATION_RE, identification_id)
    return bool(v2_match)


def start_ubble_workflow(
    user: users_models.User, first_name: str, last_name: str, redirect_url: str, webhook_url: str | None = None
) -> HttpUrl | None:
    if webhook_url is None:
        webhook_url = flask.url_for("Public API.ubble_v2_webhook_update_application_status", _external=True)

    ubble_fraud_check = _get_last_ubble_fraud_check(user)
    if ubble_fraud_check is not None and _should_reattempt_identity_verification(ubble_fraud_check):
        content = _reattempt_identity_verification(ubble_fraud_check, first_name, last_name, redirect_url, webhook_url)
        _update_identity_fraud_check(ubble_fraud_check, content)
        batch_notification.track_identity_check_started_event(ubble_fraud_check.user.id, ubble_fraud_check.type)
    else:
        content = ubble.create_and_start_identity_verification(first_name, last_name, redirect_url, webhook_url)
        subscription_api.initialize_identity_fraud_check(
            eligibility_type=user.eligibility,
            fraud_check_type=fraud_models.FraudCheckType.UBBLE,
            identity_content=content,
            third_party_id=str(content.identification_id),
            user=user,
        )

    return content.identification_url


def _get_last_ubble_fraud_check(user: users_models.User) -> fraud_models.BeneficiaryFraudCheck | None:
    ubble_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == fraud_models.FraudCheckType.UBBLE
    ]
    last_ubble_fraud_check = next((fraud_check for fraud_check in reversed(ubble_fraud_checks)), None)
    return last_ubble_fraud_check


def _should_reattempt_identity_verification(fraud_check: fraud_models.BeneficiaryFraudCheck) -> bool:
    return is_v2_identification(fraud_check.thirdPartyId) and fraud_check.status in [
        fraud_models.FraudCheckStatus.STARTED,
        fraud_models.FraudCheckStatus.PENDING,
        fraud_models.FraudCheckStatus.SUSPICIOUS,
    ]


def _reattempt_identity_verification(
    ubble_fraud_check: fraud_models.BeneficiaryFraudCheck,
    first_name: str,
    last_name: str,
    redirect_url: str,
    webhook_url: str,
) -> fraud_models.UbbleContent:
    ubble_content = ubble_fraud_check.source_data()
    assert isinstance(ubble_content, fraud_models.UbbleContent)

    identification_id = ubble_content.identification_id
    if not identification_id:
        ubble_content = _create_ubble_identification(
            ubble_content=ubble_content,
            email=ubble_fraud_check.user.email,
            first_name=first_name,
            last_name=last_name,
            redirect_url=redirect_url,
            webhook_url=webhook_url,
        )
        identification_id = ubble_content.identification_id

    try:
        identification_url = ubble.create_identity_verification_attempt(identification_id, redirect_url)
    except requests_utils.ExternalAPIException as e:
        ubble_response_status_code = e.args[0].get("status_code") if e.args else None
        has_state_conflict = ubble_response_status_code == 409
        if has_state_conflict:
            update_ubble_workflow(ubble_fraud_check)

        raise

    ubble_content.identification_url = identification_url

    return ubble_content


def _create_ubble_identification(
    *,
    ubble_content: fraud_models.UbbleContent,
    email: str,
    first_name: str,
    last_name: str,
    redirect_url: str,
    webhook_url: str,
) -> fraud_models.UbbleContent:
    applicant_id = ubble_content.applicant_id
    if not applicant_id:
        external_applicant_id = ubble_content.external_applicant_id
        if not external_applicant_id:
            raise ValueError(
                "An Ubble v2 content must have either the identification_id, applicant_id or external_applicant_id defined"
            )

        applicant_id = ubble.create_applicant(external_applicant_id, email)

    new_ubble_content = ubble.create_identity_verification(
        applicant_id, first_name, last_name, redirect_url, webhook_url
    )
    return new_ubble_content


def _update_identity_fraud_check(
    fraud_check: fraud_models.BeneficiaryFraudCheck, content: fraud_models.UbbleContent
) -> None:
    fraud_check.thirdPartyId = content.identification_id or ""

    if is_v2_identification(content.identification_id):
        if not fraud_check.resultContent:
            fraud_check.resultContent = {}
        fraud_check.resultContent.update(**content.dict(exclude_none=True))
    else:
        fraud_check.resultContent = content.dict(exclude_none=True)

    pcapi_repository.save(fraud_check)


def get_most_relevant_ubble_error(
    reason_codes: list[fraud_models.FraudReasonCode],
) -> fraud_models.FraudReasonCode | None:
    return next(
        iter(
            sorted(
                reason_codes,
                key=lambda reason_code: (
                    errors.UBBLE_CODE_ERROR_MAPPING[reason_code].priority
                    if reason_code in errors.UBBLE_CODE_ERROR_MAPPING
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
        ubble_content = _get_content(fraud_check.thirdPartyId)
    except requests_utils.ExternalAPIException:
        fraud_check.idPicturesStored = False
        pcapi_repository.save(fraud_check)
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
        pcapi_repository.save(fraud_check)
        raise exception_during_process

    fraud_check.idPicturesStored = True
    pcapi_repository.save(fraud_check)


def _get_content(identification_id: str) -> fraud_models.UbbleContent:
    if is_v2_identification(identification_id):
        return ubble.get_identity_verification(identification_id)
    return ubble.get_content(identification_id)


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


def update_pending_ubble_applications(dry_run: bool = True) -> None:
    """
    Sometimes the ubble webhook does not reach our API. This is a problem because the application is still pending.
    We want to be able to retrieve the processed applications and update the status of the application anyway.
    """
    pending_ubble_application_counter = 0
    for pending_ubble_application_fraud_checks in _get_pending_fraud_checks_pages():
        pending_ubble_application_counter += len(pending_ubble_application_fraud_checks)
        for fraud_check in pending_ubble_application_fraud_checks:
            try:
                update_ubble_workflow(fraud_check)
            except Exception:
                logger.error(
                    "Error while updating pending ubble application",
                    extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId},
                )
                continue
            db.session.refresh(fraud_check)
            if fraud_check.status == fraud_models.FraudCheckStatus.PENDING:
                logger.error(
                    "Pending ubble application still pending after 12 hours. This is a problem on the Ubble side.",
                    extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId},
                )

    if pending_ubble_application_counter > 0:
        logger.warning(
            "Found %d pending ubble application older than 12 hours and tried to update them.",
            pending_ubble_application_counter,
        )
    else:
        logger.info("No pending ubble application found older than 12 hours. This is good.")


def _get_pending_fraud_checks_pages() -> typing.Generator[list[fraud_models.BeneficiaryFraudCheck], None, None]:
    # Ubble guarantees an application is processed after 3 hours.
    # We give ourselves some extra time and we retrieve the applications that are still pending after 12 hours.
    twelve_hours_ago = datetime.date.today() - datetime.timedelta(hours=12)
    last_fraud_check_id = 0
    max_ubble_fraud_check_id = (
        db.session.query(sa.func.max(fraud_models.BeneficiaryFraudCheck.id))
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.dateCreated < twelve_hours_ago,
        )
        .scalar()
    )

    pending_fraud_check_query = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.status.in_(
                [fraud_models.FraudCheckStatus.STARTED, fraud_models.FraudCheckStatus.PENDING]
            ),
        )
        .options(
            sa_orm.joinedload(fraud_models.BeneficiaryFraudCheck.user)
            .selectinload(users_models.User.deposits)
            .selectinload(finance_models.Deposit.recredits)
        )
    )

    has_next_page = True
    while has_next_page:
        upper_fraud_check_page_id = last_fraud_check_id + PAGE_SIZE
        pending_fraud_check_page = pending_fraud_check_query.filter(
            fraud_models.BeneficiaryFraudCheck.id >= last_fraud_check_id,
            fraud_models.BeneficiaryFraudCheck.id < upper_fraud_check_page_id,
        ).all()

        yield pending_fraud_check_page

        has_next_page = upper_fraud_check_page_id <= max_ubble_fraud_check_id
        last_fraud_check_id = upper_fraud_check_page_id
