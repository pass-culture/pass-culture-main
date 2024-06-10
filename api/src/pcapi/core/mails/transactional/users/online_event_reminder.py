import datetime
import logging

import sqlalchemy as sa

from pcapi.core import mails
from pcapi.core.bookings import models as booking_models
from pcapi.core.mails import transactional as mails_transactional
from pcapi.core.mails.models import TransactionalEmailData
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


class OnlineEventReminderData:
    event_hour: datetime.datetime | None
    offer_name: str
    offer_url: str
    recipients: list[str]
    booking_id: int
    withdrawal_details: str

    def __init__(self, booking: booking_models.Booking) -> None:
        offer = booking.stock.offer
        if booking.stock.beginningDatetime:
            self.event_hour = date_utils.utc_datetime_to_department_timezone(
                booking.stock.beginningDatetime,
                offer.departementCode,
            )
        else:
            self.event_hour = None

        self.offer_name = offer.name
        self.offer_url = offer.url
        self.recipients = []
        self.booking_id = booking.id
        self.withdrawal_details = offer.withdrawalDetails

    def add_recipient(self, email: str) -> None:
        self.recipients.append(email)


def _get_online_reminder_data(data: OnlineEventReminderData) -> TransactionalEmailData | None:
    if not data.event_hour:
        logger.exception("Cannot send reminder without event hour", extra={"data": data})
        return None

    return TransactionalEmailData(
        template=mails_transactional.sendinblue_template_ids.TransactionalEmail.ONLINE_EVENT_REMINDER.value,
        params={
            "OFFER_NAME": data.offer_name,
            "DIGITAL_OFFER_URL": data.offer_url,
            "EVENT_HOUR": data.event_hour.strftime("%Hh%M"),
            "OFFER_WITHDRAWAL_DETAILS": data.withdrawal_details,
        },
    )


def _get_online_bookings_happening_soon() -> sa.orm.query.Query:
    """
    'Soon' means in the next hour but not in the next 30 minutes.
    This is to send the reminder at least 30 minutes before the event starts.
    """
    now = datetime.datetime.utcnow()
    # We normalize the minute to 0 or 30 to get the next-next 30 minutes
    normalized_minute = 0 if now.minute < 30 else 30
    normalized_now = now.replace(minute=normalized_minute, second=0, microsecond=0)

    in_30_minutes = normalized_now + datetime.timedelta(minutes=30)
    in_1_hour = normalized_now + datetime.timedelta(hours=1)
    bookings_query = (
        booking_models.Booking.query.join(Stock)
        .join(Offer)
        .join(Venue)
        .options(
            sa.orm.joinedload(booking_models.Booking.user, innerjoin=True),
            sa.orm.contains_eager(booking_models.Booking.stock).contains_eager(Stock.offer).contains_eager(Offer.venue),
        )
        .filter(
            booking_models.Booking.status == booking_models.BookingStatus.CONFIRMED,
            Stock.beginningDatetime >= in_30_minutes,
            Stock.beginningDatetime < in_1_hour,
            Offer.isEvent,
            Offer.isDigital,
        )
    )

    return bookings_query


def _get_email_data_by_stock(bookings_query: sa.orm.query.Query) -> dict[str, OnlineEventReminderData]:
    email_data_by_stock = {}
    for booking in bookings_query:
        if booking.stockId not in email_data_by_stock:
            email_data_by_stock[booking.stockId] = OnlineEventReminderData(booking=booking)
        email_data_by_stock[booking.stockId].add_recipient(booking.user.email)
    return email_data_by_stock


def _send_email_by_stock(email_data_by_stock: dict[str, OnlineEventReminderData]) -> None:
    for data in email_data_by_stock.values():
        email_data = _get_online_reminder_data(data)
        if not email_data:
            continue
        for email in data.recipients:
            # We send emails separately because we want to be able to cancel a single email if a user cancels their booking
            mails.send(recipients=[email], data=email_data)


def send_online_event_event_reminder() -> None:
    bookings_query = _get_online_bookings_happening_soon()
    email_data_by_stock = _get_email_data_by_stock(bookings_query)
    _send_email_by_stock(email_data_by_stock)
