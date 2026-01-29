import datetime
import logging
import mimetypes
import os
import pathlib
import re
import shutil
import tempfile
import typing
from functools import partial

import flask
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from pydantic.v1.networks import HttpUrl

import pcapi.core.external.batch as batch_notification
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.subscription.ubble.constants as ubble_fraud_constants
from pcapi.connectors.beneficiaries import outscale
from pcapi.connectors.beneficiaries import ubble
from pcapi.connectors.serialization import ubble_serializers
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.external.batch import track_ubble_ko_event
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud.exceptions import IncompatibleFraudCheckStatus
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.exceptions import BeneficiaryFraudCheckMissingException
from pcapi.core.subscription.ubble import fraud_check_api as ubble_fraud_api
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.tasks import ubble_tasks
from pcapi.utils import requests as requests_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import is_managed_transaction
from pcapi.utils.transaction_manager import on_commit

from . import errors
from . import exceptions
from . import messages


logger = logging.getLogger(__name__)
PAGE_SIZE = 20_000

PENDING_STATUSES = [
    ubble_schemas.UbbleIdentificationStatus.PROCESSING,
    ubble_schemas.UbbleIdentificationStatus.CHECKS_IN_PROGRESS,
]
CANCELED_STATUSES = [
    ubble_schemas.UbbleIdentificationStatus.INCONCLUSIVE,
    ubble_schemas.UbbleIdentificationStatus.REFUSED,
    ubble_schemas.UbbleIdentificationStatus.ABORTED,
    ubble_schemas.UbbleIdentificationStatus.EXPIRED,
]
CONCLUSIVE_STATUSES = [
    ubble_schemas.UbbleIdentificationStatus.APPROVED,
    ubble_schemas.UbbleIdentificationStatus.RETRY_REQUIRED,
    ubble_schemas.UbbleIdentificationStatus.DECLINED,
    ubble_schemas.UbbleIdentificationStatus.PROCESSED,
]


def update_ubble_workflow_with_status(
    fraud_check: subscription_models.BeneficiaryFraudCheck, status: ubble_schemas.UbbleIdentificationStatus
) -> None:
    """
    Checks if a Ubble network call is needed according to the status returned by the Ubble webhook.

    Ubble's rate limit of 200 requests/minute can be easily reached during peak hours through
    the native app causing an influx of webhook notifications, plus recovery scripts.
    """
    if status in PENDING_STATUSES:
        fraud_check.status = subscription_models.FraudCheckStatus.PENDING
        fraud_check.updatedAt = datetime.datetime.now(datetime.timezone.utc)
        return

    if status in CANCELED_STATUSES:
        fraud_check.status = subscription_models.FraudCheckStatus.CANCELED
        fraud_check.updatedAt = datetime.datetime.now(datetime.timezone.utc)
        return

    if status not in CONCLUSIVE_STATUSES:
        return

    update_ubble_workflow(fraud_check)


def update_ubble_workflow(fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    from pcapi.core.subscription.ubble import tasks as celery_tasks

    content = _get_content(fraud_check.thirdPartyId)
    _fill_missing_content_test_fields(content, fraud_check)

    _update_identity_fraud_check(fraud_check, content)

    user = fraud_check.user
    status = content.status
    if status in PENDING_STATUSES:
        fraud_check.status = subscription_models.FraudCheckStatus.PENDING
        fraud_check.updatedAt = datetime.datetime.now(datetime.timezone.utc)
        return

    if status in CANCELED_STATUSES:
        fraud_check.status = subscription_models.FraudCheckStatus.CANCELED
        fraud_check.updatedAt = datetime.datetime.now(datetime.timezone.utc)
        return

    if status not in CONCLUSIVE_STATUSES:
        return

    fraud_check = subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(
        user, fraud_check, content
    )
    try:
        ubble_fraud_api.on_ubble_result(fraud_check)
    except Exception as exc:
        logger.exception("Error on Ubble fraud check result: %s", extra={"user_id": user.id, "exc": exc})
        return

    subscription_api.update_user_birth_date_if_not_beneficiary(user, content.get_birth_date())

    if fraud_check.status != subscription_models.FraudCheckStatus.OK:
        handle_validation_errors(user, fraud_check)
        return

    if FeatureToggle.WIP_ASYNCHRONOUS_CELERY_UBBLE.is_active():
        celery_payload = ubble_schemas.StoreIdPicturePayload(identification_id=fraud_check.thirdPartyId)
        on_commit(partial(celery_tasks.store_id_pictures_task.delay, celery_payload.model_dump()))
    else:
        payload = ubble_tasks.StoreIdPictureRequest(identification_id=fraud_check.thirdPartyId)
        on_commit(partial(ubble_tasks.store_id_pictures_task.delay, payload))

    try:
        is_activated = subscription_api.activate_beneficiary_if_no_missing_step(user=user)
    except Exception as e:
        logger.exception("Failure after ubble successful result", extra={"user_id": user.id, "exc": str(e)})
        return

    if not is_activated:
        external_attributes_api.update_external_user(user)


def _fill_missing_content_test_fields(
    content: ubble_schemas.UbbleContent, fraud_check: subscription_models.BeneficiaryFraudCheck
) -> None:
    previous_ubble_content = fraud_check.source_data()
    assert isinstance(previous_ubble_content, ubble_schemas.UbbleContent)

    user = fraud_check.user
    is_test_identification = (
        ubble_fraud_api.does_match_ubble_test_names(content) or previous_ubble_content.external_applicant_id is not None
    )
    should_fill_content = is_test_identification and content.status == ubble_schemas.UbbleIdentificationStatus.APPROVED
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
    from pcapi.core.subscription.ubble import tasks as ubble_tasks

    if webhook_url is None:
        webhook_url = flask.url_for("Public API.ubble_v2_webhook_update_application_status", _external=True)

    ubble_fraud_check = _get_last_ubble_fraud_check(user)
    if ubble_fraud_check is None or not _should_reattempt_identity_verification(ubble_fraud_check):
        content = ubble.create_and_start_identity_verification(first_name, last_name, redirect_url, webhook_url)
        subscription_api.initialize_identity_fraud_check(
            eligibility_type=user.eligibility,
            fraud_check_type=subscription_models.FraudCheckType.UBBLE,
            identity_content=content,
            third_party_id=str(content.identification_id),
            user=user,
        )
        return content.identification_url

    try:
        content = _reattempt_identity_verification(ubble_fraud_check, first_name, last_name, redirect_url, webhook_url)
    except ubble.UbbleConflictError:
        # resync the identity verification
        ubble_tasks.update_ubble_workflow_task.delay(
            payload=ubble_schemas.UpdateWorkflowPayload(beneficiary_fraud_check_id=ubble_fraud_check.id).model_dump()
        )

        raise

    _update_identity_fraud_check(ubble_fraud_check, content)
    batch_notification.track_identity_check_started_event(ubble_fraud_check.user.id, ubble_fraud_check.type)

    return content.identification_url


def _get_last_ubble_fraud_check(user: users_models.User) -> subscription_models.BeneficiaryFraudCheck | None:
    ubble_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == subscription_models.FraudCheckType.UBBLE
    ]
    last_ubble_fraud_check = next((fraud_check for fraud_check in reversed(ubble_fraud_checks)), None)
    return last_ubble_fraud_check


def _should_reattempt_identity_verification(fraud_check: subscription_models.BeneficiaryFraudCheck) -> bool:
    return is_v2_identification(fraud_check.thirdPartyId) and fraud_check.status in [
        subscription_models.FraudCheckStatus.STARTED,
        subscription_models.FraudCheckStatus.PENDING,
        subscription_models.FraudCheckStatus.SUSPICIOUS,
    ]


def _reattempt_identity_verification(
    ubble_fraud_check: subscription_models.BeneficiaryFraudCheck,
    first_name: str,
    last_name: str,
    redirect_url: str,
    webhook_url: str,
) -> ubble_schemas.UbbleContent:
    ubble_content = ubble_fraud_check.source_data()
    assert isinstance(ubble_content, ubble_schemas.UbbleContent)

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

    identification_url = ubble.create_identity_verification_attempt(identification_id, redirect_url)
    ubble_content.identification_url = identification_url

    return ubble_content


def _create_ubble_identification(
    *,
    ubble_content: ubble_schemas.UbbleContent,
    email: str,
    first_name: str,
    last_name: str,
    redirect_url: str,
    webhook_url: str,
) -> ubble_schemas.UbbleContent:
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
    fraud_check: subscription_models.BeneficiaryFraudCheck, content: ubble_schemas.UbbleContent
) -> None:
    fraud_check.thirdPartyId = content.identification_id or ""

    if is_v2_identification(content.identification_id):
        if not fraud_check.resultContent:
            fraud_check.resultContent = {}
        fraud_check.resultContent.update(**content.dict(exclude_none=True))
    else:
        fraud_check.resultContent = content.dict(exclude_none=True)

    db.session.add(fraud_check)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()


def get_most_relevant_ubble_error(
    reason_codes: list[subscription_models.FraudReasonCode],
) -> subscription_models.FraudReasonCode | None:
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


def _requires_reminder(error_code: subscription_models.FraudReasonCode | None) -> bool:
    return (
        error_code in ubble_fraud_constants.REASON_CODE_REQUIRING_IMMEDIATE_NOTIFICATION_REMINDER
        or error_code in ubble_fraud_constants.REASON_CODE_REQUIRING_IMMEDIATE_EMAIL_REMINDER
    )


def _dispatch_reminder(user: users_models.User, error_code: subscription_models.FraudReasonCode | None) -> None:
    if error_code in ubble_fraud_constants.REASON_CODE_REQUIRING_IMMEDIATE_EMAIL_REMINDER:
        transactional_mails.send_subscription_document_error_email(user.email, error_code)
    if error_code in ubble_fraud_constants.REASON_CODE_REQUIRING_IMMEDIATE_NOTIFICATION_REMINDER:
        track_ubble_ko_event(user.id, error_code)


def handle_validation_errors(
    user: users_models.User,
    fraud_check: subscription_models.BeneficiaryFraudCheck,
) -> None:
    error_codes = fraud_check.reasonCodes or []
    relevant_error_code = get_most_relevant_ubble_error(error_codes)
    if _requires_reminder(relevant_error_code):
        _dispatch_reminder(user, relevant_error_code)
    elif subscription_models.FraudReasonCode.DUPLICATE_USER in error_codes:
        source_data = fraud_check.source_data()
        assert isinstance(source_data, subscription_schemas.IdentityCheckContent)
        transactional_mails.send_duplicate_beneficiary_email(
            user, source_data, subscription_models.FraudReasonCode.DUPLICATE_USER
        )
    elif subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in error_codes:
        source_data = fraud_check.source_data()
        assert isinstance(source_data, subscription_schemas.IdentityCheckContent)
        transactional_mails.send_duplicate_beneficiary_email(
            user, source_data, subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER
        )


def archive_id_pictures_with_recovery(fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    try:
        archive_ubble_user_id_pictures(fraud_check.thirdPartyId)
    except ubble.UbbleAssetExpiredError:
        recover_id_pictures_asset(fraud_check)
        archive_ubble_user_id_pictures(fraud_check.thirdPartyId)


def recover_id_pictures_asset(fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    identification_id = fraud_check.thirdPartyId
    logger.warning("Recovering the archiving of Ubble identification %s", identification_id)

    attempts = ubble.get_attempts(identification_id)
    succesful_attempts = [
        attempt for attempt in attempts if attempt.status == ubble_serializers.AttemptStatus.COMPLETED
    ]
    if not succesful_attempts:
        logger.error(
            "Succesful attempt of Ubble identification %s is not in the first page. Pagination must be implemented.",
            identification_id,
        )
        return

    succesful_attempt = succesful_attempts[0]
    assets = ubble.get_attempt_assets(identification_id, succesful_attempt.id)

    with atomic():
        if not fraud_check.resultContent:
            fraud_check.resultContent = {}

        front_image_url = assets.get(ubble_serializers.AssetType.DOCUMENT_FRONT_IMAGE)
        if front_image_url:
            fraud_check.resultContent["signed_image_front_url"] = front_image_url

        back_image_url = assets.get(ubble_serializers.AssetType.DOCUMENT_BACK_IMAGE)
        if back_image_url:
            fraud_check.resultContent["signed_image_back_url"] = back_image_url


def archive_ubble_user_id_pictures(identification_id: str) -> None:
    fraud_check = ubble_fraud_api.get_ubble_fraud_check(identification_id)
    if not fraud_check:
        raise BeneficiaryFraudCheckMissingException(
            f"No validated Identity fraudCheck found with identification_id {identification_id}"
        )

    if fraud_check.status is not subscription_models.FraudCheckStatus.OK:
        raise IncompatibleFraudCheckStatus(
            f"Fraud check status {fraud_check.status} is incompatible with pictures archives for identification_id {identification_id}"
        )

    if FeatureToggle.WIP_ASYNCHRONOUS_CELERY_UBBLE.is_active():
        ubble_content = fraud_check.source_data()
        if not isinstance(ubble_content, ubble_schemas.UbbleContent):
            raise ValueError(f"UbbleContent was expected while {type(ubble_content)} was given")
    else:
        ubble_content = _get_content(fraud_check.thirdPartyId)

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
        raise exception_during_process

    with atomic():
        fraud_check.idPicturesStored = True


def _get_content(identification_id: str) -> ubble_schemas.UbbleContent:
    if is_v2_identification(identification_id):
        return ubble.get_identity_verification(identification_id)
    return ubble.get_content(identification_id)


def _download_and_store_ubble_picture(
    fraud_check: subscription_models.BeneficiaryFraudCheck, http_url: HttpUrl, face_name: str
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
    fraud_check: subscription_models.BeneficiaryFraudCheck, face_name: str, mime_type: str | None
) -> str:
    if mime_type is None:
        mime_type = "image/png"  # ubble default picture type is png
    extension = mimetypes.guess_extension(mime_type, strict=True)
    return f"{fraud_check.userId}-{fraud_check.thirdPartyId}-{face_name}{extension}"


def get_ubble_subscription_message(
    ubble_fraud_check: subscription_models.BeneficiaryFraudCheck,
) -> subscription_schemas.SubscriptionMessage | None:
    if ubble_fraud_check.status == subscription_models.FraudCheckStatus.PENDING:
        return messages.get_application_pending_message(ubble_fraud_check.updatedAt)

    if ubble_fraud_check.status in (
        subscription_models.FraudCheckStatus.SUSPICIOUS,
        subscription_models.FraudCheckStatus.KO,
        subscription_models.FraudCheckStatus.ERROR,
    ):
        if subscription_api.can_retry_identity_fraud_check(ubble_fraud_check):
            return messages.get_ubble_retryable_message(
                ubble_fraud_check.reasonCodes or [], ubble_fraud_check.updatedAt
            )
        return messages.get_ubble_not_retryable_message(ubble_fraud_check)

    return None


def recover_pending_ubble_applications(dry_run: bool = True) -> None:
    """
    Sometimes the ubble webhook does not reach our API. This is a problem because the application is still pending.
    We want to be able to retrieve the processed applications and update the status of the application anyway.
    """
    from pcapi.core.subscription.ubble import tasks as ubble_tasks

    if FeatureToggle.WIP_ASYNCHRONOUS_CELERY_UBBLE.is_active():
        started_fraud_checks = 0
        pending_fraud_checks = 0

        stale_ubble_fraud_check_ids = _get_stale_fraud_checks_id_and_status(ubble_tasks.UBBLE_TASK_RATE_LIMIT)
        for fraud_check_id, fraud_check_status in stale_ubble_fraud_check_ids:
            ubble_tasks.update_ubble_workflow_task.delay(
                payload=ubble_schemas.UpdateWorkflowPayload(beneficiary_fraud_check_id=fraud_check_id).model_dump()
            )

            if fraud_check_status == subscription_models.FraudCheckStatus.STARTED:
                started_fraud_checks += 1
            if fraud_check_status == subscription_models.FraudCheckStatus.PENDING:
                pending_fraud_checks += 1

        logger.warning(
            "Found %d stale ubble application with %d currently started and %d currently pending",
            len(stale_ubble_fraud_check_ids),
            started_fraud_checks,
            pending_fraud_checks,
        )
        return

    pending_ubble_application_counter = 0
    for pending_ubble_fraud_check_ids in _get_pending_fraud_checks_pages():
        pending_ubble_application_counter += len(pending_ubble_fraud_check_ids)
        for fraud_check in pending_ubble_fraud_check_ids:
            try:
                with atomic():
                    update_ubble_workflow(fraud_check)
            except Exception as exc:
                logger.error(
                    "Error while updating pending ubble application",
                    extra={"fraud_check_id": fraud_check.id, "ubble_id": fraud_check.thirdPartyId, "exc": str(exc)},
                )
                continue
            db.session.refresh(fraud_check)
            if fraud_check.status == subscription_models.FraudCheckStatus.PENDING:
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


def _get_stale_fraud_checks_id_and_status(
    page_size: int,
) -> typing.Sequence[sa.Row[tuple[int, subscription_models.FraudCheckStatus | None]]]:
    """
    Returns the `page_size` first stale and pending fraud checks.
    This function only returns the first page, and is meant to be called every five minutes by recovery workers.
    """
    from pcapi.celery_tasks.tasks import MAX_RETRY_DURATION
    from pcapi.core.subscription.ubble import tasks as ubble_tasks

    # Celery workers keep all rate limited tasks in memory so we need to limit task stacking lest the workers get OOMKilled
    page_size_limit = ubble_tasks.UBBLE_TASK_RATE_LIMIT * (MAX_RETRY_DURATION / 60)  # ~ 3500 elements
    if page_size > page_size_limit:
        raise ValueError(f"{page_size = } is above {page_size_limit = }")

    # Ubble guarantees an application is processed after 3 hours.
    # We give ourselves some extra time and we retrieve the applications that are still pending after 12 hours.
    twelve_hours_ago = datetime.date.today() - datetime.timedelta(hours=12)
    stale_fraud_check_ids_stmt = (
        sa.select(subscription_models.BeneficiaryFraudCheck.id, subscription_models.BeneficiaryFraudCheck.status)
        .filter(
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.UBBLE,
            subscription_models.BeneficiaryFraudCheck.status.in_(
                [subscription_models.FraudCheckStatus.STARTED, subscription_models.FraudCheckStatus.PENDING]
            ),
            subscription_models.BeneficiaryFraudCheck.updatedAt < twelve_hours_ago,
        )
        .order_by(subscription_models.BeneficiaryFraudCheck.id)
        .limit(page_size)
    )

    return db.session.execute(stale_fraud_check_ids_stmt).all()


def _get_pending_fraud_checks_pages() -> typing.Generator[list[subscription_models.BeneficiaryFraudCheck], None, None]:
    # Ubble guarantees an application is processed after 3 hours.
    # We give ourselves some extra time and we retrieve the applications that are still pending after 12 hours.
    twelve_hours_ago = datetime.date.today() - datetime.timedelta(hours=12)
    last_fraud_check_id = 0
    max_ubble_fraud_check_id = (
        db.session.query(sa.func.max(subscription_models.BeneficiaryFraudCheck.id))
        .filter(
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.UBBLE,
            subscription_models.BeneficiaryFraudCheck.dateCreated < twelve_hours_ago,
        )
        .scalar()
    )

    pending_fraud_check_query = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.UBBLE,
            subscription_models.BeneficiaryFraudCheck.status.in_(
                [subscription_models.FraudCheckStatus.STARTED, subscription_models.FraudCheckStatus.PENDING]
            ),
        )
        .options(
            sa_orm.joinedload(subscription_models.BeneficiaryFraudCheck.user)
            .selectinload(users_models.User.deposits)
            .selectinload(finance_models.Deposit.recredits)
        )
    )

    has_next_page = True
    while has_next_page:
        upper_fraud_check_page_id = last_fraud_check_id + PAGE_SIZE
        pending_fraud_check_page = pending_fraud_check_query.filter(
            subscription_models.BeneficiaryFraudCheck.id >= last_fraud_check_id,
            subscription_models.BeneficiaryFraudCheck.id < upper_fraud_check_page_id,
        ).all()

        yield pending_fraud_check_page

        has_next_page = upper_fraud_check_page_id <= max_ubble_fraud_check_id
        last_fraud_check_id = upper_fraud_check_page_id
