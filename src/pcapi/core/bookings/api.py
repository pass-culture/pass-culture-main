import base64
import datetime
import io
import logging
import typing

from PIL import Image
from flask import current_app as app
import pytz
import qrcode
import qrcode.image.svg

from pcapi.connectors import redis
from pcapi.core.bookings import conf
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.repository import generate_booking_token
from pcapi.core.offers import repository as offers_repository
from pcapi.core.users.models import User
from pcapi.domain import user_emails
from pcapi.models.feature import FeatureToggle
from pcapi.notifications.push.transactional_notifications import get_notification_data_on_booking_cancellation
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.utils.mailing import MailServiceException
from pcapi.workers.push_notification_job import send_transactional_notification_job

from . import validation


logger = logging.getLogger(__name__)

QR_CODE_PASS_CULTURE_VERSION = "v2"
QR_CODE_VERSION = 2
QR_CODE_BOX_SIZE = 5
QR_CODE_BOX_BORDER = 1


def book_offer(
    beneficiary: User,
    stock_id: int,
    quantity: int,
) -> Booking:
    """Return a booking or raise an exception if it's not possible."""
    # The call to transaction here ensures we free the FOR UPDATE lock
    # on the stock if validation issues an exception
    with transaction():
        stock = offers_repository.get_and_lock_stock(stock_id=stock_id)
        validation.check_can_book_free_offer(beneficiary, stock)
        validation.check_offer_already_booked(beneficiary, stock.offer)
        validation.check_quantity(stock.offer, quantity)
        validation.check_stock_is_bookable(stock)
        total_amount = quantity * stock.price
        validation.check_expenses_limits(beneficiary, total_amount, stock.offer)

        # FIXME (dbaty, 2020-10-20): if we directly set relations (for
        # example with `booking.user = beneficiary`) instead of foreign keys,
        # the session tries to add the object when `get_user_expenses()`
        # is called because autoflush is enabled. As such, the PostgreSQL
        # exceptions (tooManyBookings and insufficientFunds) may raise at
        # this point and will bubble up. If we want them to be caught, we
        # have to set foreign keys, so that the session is NOT autoflushed
        # in `get_user_expenses` and is only committed in `repository.save()`
        # where exceptions are caught. Since we are using flask-sqlalchemy,
        # I don't think that we should use autoflush, nor should we use
        # the `pcapi.repository.repository` module.
        booking = Booking(
            userId=beneficiary.id,
            stockId=stock.id,
            amount=stock.price,
            quantity=quantity,
            token=generate_booking_token(),
        )

        booking.dateCreated = datetime.datetime.utcnow()
        booking.confirmationDate = compute_confirmation_date(stock.beginningDatetime, booking.dateCreated)

        stock.dnBookedQuantity += booking.quantity

        repository.save(booking, stock)

    try:
        user_emails.send_booking_recap_emails(booking)
    except MailServiceException as error:
        logger.exception("Could not send booking=%s confirmation email to offerer: %s", booking.id, error)
    try:
        user_emails.send_booking_confirmation_email_to_beneficiary(booking)
    except MailServiceException as error:
        logger.exception("Could not send booking=%s confirmation email to beneficiary: %s", booking.id, error)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    return booking


def cancel_booking_by_beneficiary(user: User, booking: Booking) -> None:
    if not user.isBeneficiary:
        raise RuntimeError("Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s" % user)
    validation.check_beneficiary_can_cancel_booking(user, booking)

    booking.isCancelled = True
    booking.cancellationReason = BookingCancellationReasons.BENEFICIARY
    repository.save(booking)

    try:
        user_emails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)
    except MailServiceException as error:
        logger.exception("Could not send booking=%s cancellation emails to user and offerer: %s", booking.id, error)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=booking.stock.offerId)


def cancel_booking_by_offerer(booking: Booking) -> None:
    validation.check_offerer_can_cancel_booking(booking)
    booking.isCancelled = True
    booking.cancellationReason = BookingCancellationReasons.OFFERER
    repository.save(booking)

    send_transactional_notification_job.delay(get_notification_data_on_booking_cancellation([booking]))

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=booking.stock.offerId)


def mark_as_used(booking: Booking, uncancel=False) -> None:
    """Mark a booking as used.

    The ``uncancel`` argument should be provided only if the booking
    has been cancelled by mistake or fraudulently after the offer was
    retrieved (for example, when a beneficiary retrieved a book from a
    library and then cancelled their booking before the library marked
    it as used).
    """
    if uncancel:
        booking.isCancelled = False
        booking.cancellationReason = None
    validation.check_is_usable(booking)
    booking.isUsed = True
    booking.dateUsed = datetime.datetime.utcnow()
    repository.save(booking)


def mark_as_unused(booking: Booking) -> None:
    validation.check_can_be_mark_as_unused(booking)
    booking.isUsed = False
    booking.dateUsed = None
    repository.save(booking)


def generate_qr_code(booking_token: str, offer_extra_data: typing.Dict) -> str:
    qr = qrcode.QRCode(
        version=QR_CODE_VERSION,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=QR_CODE_BOX_SIZE,
        border=QR_CODE_BOX_BORDER,
    )

    product_isbn = ""
    if offer_extra_data and "isbn" in offer_extra_data:
        product_isbn = offer_extra_data["isbn"]

    data = f"PASSCULTURE:{QR_CODE_PASS_CULTURE_VERSION};"

    if product_isbn != "":
        data += f"EAN13:{product_isbn};"

    data += f"TOKEN:{booking_token}"

    qr.add_data(data)
    image = qr.make_image(fill_color="black", back_color="white")
    return _convert_image_to_base64(image)


def _convert_image_to_base64(image: Image) -> str:
    image_as_bytes = io.BytesIO()
    image.save(image_as_bytes)
    image_as_base64 = base64.b64encode(image_as_bytes.getvalue())
    return f'data:image/png;base64,{str(image_as_base64, encoding="utf-8")}'


def compute_confirmation_date(
    event_beginning: typing.Optional[datetime.datetime], booking_creation_or_event_edition: datetime.datetime
) -> typing.Optional[datetime.datetime]:
    if event_beginning:
        if event_beginning.tzinfo:
            tz_naive_event_beginning = event_beginning.astimezone(pytz.utc)
            tz_naive_event_beginning = tz_naive_event_beginning.replace(tzinfo=None)
        else:
            tz_naive_event_beginning = event_beginning
        before_event_limit = tz_naive_event_beginning - conf.CONFIRM_BOOKING_BEFORE_EVENT_DELAY
        after_booking_or_event_edition_limit = (
            booking_creation_or_event_edition + conf.CONFIRM_BOOKING_AFTER_CREATION_DELAY
        )
        earliest_date_in_cancellation_period = min(before_event_limit, after_booking_or_event_edition_limit)
        latest_date_between_earliest_date_in_cancellation_period_and_booking_creation_or_event_edition = max(
            earliest_date_in_cancellation_period, booking_creation_or_event_edition
        )
        return latest_date_between_earliest_date_in_cancellation_period_and_booking_creation_or_event_edition
    return None


def update_confirmation_dates(
    bookings_to_update: typing.List[Booking], new_beginning_datetime: datetime.datetime
) -> typing.List[Booking]:
    for booking in bookings_to_update:
        booking.confirmationDate = compute_confirmation_date(
            event_beginning=new_beginning_datetime, booking_creation_or_event_edition=datetime.datetime.utcnow()
        )
    repository.save(*bookings_to_update)
    return bookings_to_update
