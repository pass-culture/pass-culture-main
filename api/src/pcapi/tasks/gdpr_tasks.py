from datetime import datetime
from io import BytesIO
import logging
import zipfile

from sqlalchemy.orm import joinedload

from pcapi import repository
from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import models as history_models
from pcapi.core.history.api import add_action
from pcapi.core.history.models import ActionType
from pcapi.core.mails import get_raw_contact_data
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.tasks.decorator import task

from .serialization import gdpr_tasks as serializers


logger = logging.getLogger(__name__)


class ExtractNotFound(Exception):
    pass


class ExtractNotPermitted(Exception):
    pass


def _get_and_update_extract(extract_id: int) -> users_models.GdprUserDataExtract:
    extract = (
        users_models.GdprUserDataExtract.query.filter(
            users_models.GdprUserDataExtract.id == extract_id,
            users_models.GdprUserDataExtract.dateProcessed.is_(None),
        )
        .options(
            joinedload(users_models.GdprUserDataExtract.user),
            joinedload(users_models.GdprUserDataExtract.authorUser),
        )
        .one_or_none()
    )

    if not extract or extract.expirationDate > datetime.utcnow():
        raise ExtractNotFound()

    if not (extract.authorUser.isActive and extract.authorUser.has_admin_role):
        raise ExtractNotPermitted(extract.authorUser.id, extract.user.id)

    extract.dateProcessed = datetime.utcnow()
    return extract


def _extract_marketing_data(user: users_models.User) -> serializers.Marketing:
    notification_subscriptions = user.notificationSubscriptions or {}
    return serializers.Marketing(
        marketingEmails=notification_subscriptions.get("marketing_email") or False,
        marketingNotifications=notification_subscriptions.get("marketing_push") or False,
    )


def _extract_devices_history(user: users_models.User) -> list[serializers.LoginDeviceHistorySerializer]:
    login_devices_data = (
        users_models.LoginDeviceHistory.query.filter(users_models.LoginDeviceHistory.user == user)
        .order_by(users_models.LoginDeviceHistory.id)
        .all()
    )
    return [serializers.LoginDeviceHistorySerializer.from_orm(data) for data in login_devices_data]


def _extract_deposits(user: users_models.User) -> list[serializers.DepositSerializer]:
    deposits_data = (
        finance_models.Deposit.query.filter(finance_models.Deposit.user == user)
        .order_by(finance_models.Deposit.id)
        .all()
    )
    return [serializers.DepositSerializer.from_orm(d) for d in deposits_data]


def _extract_email_history(user: users_models.User) -> list[serializers.EmailHistory]:
    emails = (
        users_models.UserEmailHistory.query.filter(
            users_models.UserEmailHistory.user == user,
            users_models.UserEmailHistory.eventType.in_(
                [
                    users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST,
                    users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST,
                ]
            ),
        )
        .order_by(users_models.UserEmailHistory.id)
        .all()
    )
    emails_history = []
    for history in emails:
        emails_history.append(
            serializers.EmailHistory(
                oldEmail=f"{history.oldUserEmail}@{history.oldDomainEmail}",
                newEmail=f"{history.newUserEmail}@{history.newDomainEmail}",
                dateCreated=history.creationDate,
            )
        )
    return emails_history


def _extract_action_history(user: users_models.User) -> list[serializers.ActionHistorySerializer]:
    actions_history = (
        history_models.ActionHistory.query.filter(
            history_models.ActionHistory.user == user,
            history_models.ActionHistory.actionType.in_(
                [
                    history_models.ActionType.USER_SUSPENDED,
                    history_models.ActionType.USER_UNSUSPENDED,
                    history_models.ActionType.USER_PHONE_VALIDATED,
                    history_models.ActionType.USER_EMAIL_VALIDATED,
                ],
            ),
        )
        .order_by(history_models.ActionHistory.id)
        .all()
    )
    return [serializers.ActionHistorySerializer.from_orm(a) for a in actions_history]


def _extract_beneficiary_validation(user: users_models.User) -> list[serializers.BeneficiaryValidation]:
    beneficiary_fraud_checks = (
        fraud_models.BeneficiaryFraudCheck.query.filter(fraud_models.BeneficiaryFraudCheck.user == user)
        .order_by(fraud_models.BeneficiaryFraudCheck.id)
        .all()
    )
    return [serializers.BeneficiaryValidation.from_orm(b) for b in beneficiary_fraud_checks]


def _extract_booking_data(user: users_models.User) -> list[serializers.BookingSerializer]:
    bookings_data = (
        bookings_models.Booking.query.filter(
            bookings_models.Booking.user == user,
        )
        .options(
            joinedload(bookings_models.Booking.stock).joinedload(offers_models.Stock.offer),
            joinedload(bookings_models.Booking.venue),
            joinedload(bookings_models.Booking.venue).joinedload(offerers_models.Venue.managingOfferer),
        )
        .order_by(bookings_models.Booking.id)
    )
    bookings = []
    for booking_data in bookings_data:
        offerer = booking_data.venue.managingOfferer
        bookings.append(
            serializers.BookingSerializer(
                cancellationDate=booking_data.cancellationDate,
                dateCreated=booking_data.dateCreated,
                dateUsed=booking_data.dateUsed,
                quantity=booking_data.quantity,
                amount=booking_data.amount,
                status=booking_data.status,
                name=booking_data.stock.offer.name,
                venue=booking_data.venue.common_name,
                offerer=offerer.name,
            )
        )
    return bookings


def _extract_brevo_data(user: users_models.User) -> dict:
    return get_raw_contact_data(user.email)


def _dump_as_json_bytes(container: serializers.DataContainer) -> tuple[zipfile.ZipInfo, bytes]:
    json_bytes = container.json(indent=4).encode("utf-8")
    file_info = zipfile.ZipInfo(
        filename=f"{container.internal.user.firstName}_{container.internal.user.lastName}.json",
        date_time=datetime.utcnow().timetuple()[:6],
    )
    return file_info, json_bytes


def _generate_archive(container: serializers.DataContainer) -> BytesIO:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", allowZip64=False) as zip_file:
        zip_file.writestr(*_dump_as_json_bytes(container))
    buffer.seek(0)
    return buffer


def _store_archive(name: str, archive: bytes) -> None:
    store_public_object(
        folder=settings.GCP_GDPR_EXTRACT_FOLDER,
        object_id=name,
        blob=archive,
        content_type="application/zip",
        bucket=settings.GCP_GDPR_EXTRACT_BUCKET,
    )


@task(settings.GCP_GDPR_EXTRACT_QUEUE, "/gdpr/beneficiary/extract")
@repository.atomic()
def extract_beneficiary_data(payload: serializers.ExtractBeneficiaryDataRequest) -> None:
    try:
        extract = _get_and_update_extract(payload.extract_id)
        user = extract.user
        data = serializers.DataContainer(
            generationDate=datetime.utcnow(),
            internal=serializers.Internal(
                user=serializers.UserSerializer.from_orm(user),
                marketing=_extract_marketing_data(user),
                loginDevices=_extract_devices_history(user),
                emailsHistory=_extract_email_history(user),
                actionsHistory=_extract_action_history(user),
                beneficiaryValidations=_extract_beneficiary_validation(user),
                deposits=_extract_deposits(user),
                bookings=_extract_booking_data(user),
            ),
            external=serializers.External(
                brevo=_extract_brevo_data(user),
            ),
        )
        archive = _generate_archive(data)
        _store_archive(
            name=f"{extract.id}.zip",
            archive=archive.getvalue(),
        )

        add_action(
            action_type=ActionType.USER_EXTRACT_DATA,
            author=extract.authorUser,
            user=extract.user,
        )
    except ExtractNotFound:
        repository.mark_transaction_as_invalid()
        logger.exception(
            "Could not find unprocessed extract for id.",
            extra={
                "extract_id": payload.extract_id,
            },
        )
    except ExtractNotPermitted as exc:
        repository.mark_transaction_as_invalid()
        logger.exception(
            "Non active admin user tried to extract beneficiary data",
            extra={
                "extract_id": payload.extract_id,
                "author_id": exc.args[0],
                "user_id": exc.args[1],
            },
        )
