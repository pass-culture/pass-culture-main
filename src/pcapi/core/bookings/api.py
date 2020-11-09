import base64
import datetime
import io
import typing

from PIL import Image
from flask import current_app as app
import pytz
import qrcode
import qrcode.image.svg

from pcapi.connectors import redis
from pcapi.core.bookings import conf
from pcapi.core.bookings.models import Booking
from pcapi.infrastructure.services.notification.mailjet_notification_service import MailjetNotificationService
from pcapi.models.feature import FeatureToggle
from pcapi.models.recommendation import Recommendation
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.utils.mailing import send_raw_email
from pcapi.utils.token import random_token

from . import repository as booking_repository
from . import validation


QR_CODE_PASS_CULTURE_VERSION = 'v2'
QR_CODE_VERSION = 2
QR_CODE_BOX_SIZE = 5
QR_CODE_BOX_BORDER = 1


def book_offer(
    beneficiary: UserSQLEntity,
    stock: StockSQLEntity,
    quantity: int,
    recommendation: Recommendation = None,
) -> Booking:
    """Return a booking or raise an exception if it's not possible."""
    validation.check_can_book_free_offer(beneficiary, stock)
    validation.check_offer_already_booked(beneficiary, stock.offer)
    validation.check_quantity(stock.offer, quantity)
    validation.check_stock_is_bookable(stock)

    # FIXME (dbaty, 2020-11-06): this is not right. PcOject's constructor
    # should allow to call it with `Booking(stock=stock, ...)`
    booking = Booking()
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
    booking.userId = beneficiary.id
    booking.stockId = stock.id
    booking.amount = stock.price
    booking.quantity = quantity
    booking.token = random_token()
    if recommendation:
        booking.recommendationId = recommendation.id

    expenses = booking_repository.get_user_expenses(beneficiary)
    validation.check_expenses_limits(expenses, booking.total_amount, stock.offer)

    booking.dateCreated = datetime.datetime.utcnow()
    booking.confirmationDate = compute_confirmation_date(stock.beginningDatetime, booking.dateCreated)

    repository.save(booking)

    notifier = MailjetNotificationService()
    notifier.send_booking_recap(booking)
    notifier.send_booking_confirmation_to_beneficiary(booking)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    return booking


def cancel_booking_by_beneficiary(user: UserSQLEntity, booking: Booking) -> None:
    if not user.canBookFreeOffers:
        raise RuntimeError(
            "Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s" % user
        )
    validation.check_beneficiary_can_cancel_booking(user, booking)

    booking.isCancelled = True
    repository.save(booking)

    notifier = MailjetNotificationService()
    notifier.send_booking_cancellation_emails_to_user_and_offerer(
        booking=booking,
        is_offerer_cancellation=False,
        is_user_cancellation=True,
        # FIXME: we should not have to pass this argument.
        # Notification-related code should be reorganized.
        send_email=send_raw_email,
    )

    # FIXME: why do we do that when the booking is cancelled by the
    # *beneficiary*, but not when it's cancelled by the *offerer* (see
    # cancel_booking_by_offerer)?
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=booking.stock.offerId)


def cancel_booking_by_offerer(booking: Booking) -> None:
    validation.check_offerer_can_cancel_booking(booking)
    booking.isCancelled = True
    repository.save(booking)


def mark_as_used(booking: Booking) -> None:
    validation.check_is_usable(booking)
    booking.isUsed = True
    booking.dateUsed = datetime.datetime.utcnow()
    repository.save(booking)


def mark_as_unused(booking: Booking) -> None:
    validation.check_is_not_activation_booking(booking)
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

    product_isbn = ''
    if offer_extra_data and 'isbn' in offer_extra_data:
        product_isbn = offer_extra_data['isbn']

    data = f'PASSCULTURE:{QR_CODE_PASS_CULTURE_VERSION};'

    if product_isbn != '':
        data += f'EAN13:{product_isbn};'

    data += f'TOKEN:{booking_token}'

    qr.add_data(data)
    image = qr.make_image(fill_color='black', back_color='white')
    return _convert_image_to_base64(image)


def _convert_image_to_base64(image: Image) -> str:
    image_as_bytes = io.BytesIO()
    image.save(image_as_bytes)
    image_as_base64 = base64.b64encode(image_as_bytes.getvalue())
    return f'data:image/png;base64,{str(image_as_base64, encoding="utf-8")}'


def compute_confirmation_date(event_beginning: typing.Optional[datetime.datetime], booking_creation: datetime.datetime) -> typing.Optional[datetime.datetime]:
    if event_beginning:
        if event_beginning.tzinfo:
            tz_naive_event_beginning = event_beginning.astimezone(pytz.utc)
            tz_naive_event_beginning = tz_naive_event_beginning.replace(tzinfo=None)
        else:
            tz_naive_event_beginning = event_beginning
        before_event_limit = tz_naive_event_beginning - conf.CONFIRM_BOOKING_BEFORE_EVENT_DELAY
        after_booking_limit = booking_creation + conf.CONFIRM_BOOKING_AFTER_CREATION_DELAY
        earliest_date_in_cancellation_period = min(before_event_limit, after_booking_limit)
        latest_date_between_earliest_date_in_cancellation_period_and_booking_creation = max(earliest_date_in_cancellation_period, booking_creation)
        return latest_date_between_earliest_date_in_cancellation_period_and_booking_creation
    return None
