import datetime
import logging

from flask import current_app as app
import sqlalchemy as sa

from pcapi.core import mails
from pcapi.core.bookings import constants
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import transactional as mails_transactional
from pcapi.core.mails.models import TransactionalEmailData
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock


logger = logging.getLogger(__name__)


class OnlineEventReminderData:
    event_hour: datetime.datetime | None
    offer_name: str
    offer_url: str
    recipients: list[str]
    booking_id: int
    withdrawal_details: str

    def __init__(self, booking: Booking) -> None:
        stock = booking.stock
        self.event_hour = stock.beginningDatetime
        self.offer_name = stock.offer.name
        self.offer_url = stock.offer.url
        self.recipients = []
        self.booking_id = booking.id
        self.withdrawal_details = stock.offer.withdrawalDetails

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
            "BOOKING_ID": data.booking_id,
        },
        scheduled_at=data.event_hour - datetime.timedelta(minutes=30),
    )


def _get_online_events_happening_tomorrow() -> sa.orm.query.Query:
    tomorrow = datetime.datetime.utcnow().date() + datetime.timedelta(days=1)
    tomorrow_start_of_day = datetime.datetime.combine(tomorrow, datetime.time.min)
    tomorrow_end_of_day = datetime.datetime.combine(tomorrow, datetime.time.max)

    bookings_query = (
        Booking.query.join(Stock)
        .join(Offer)
        .filter(
            Stock.beginningDatetime >= tomorrow_start_of_day,
            Stock.beginningDatetime <= tomorrow_end_of_day,
            Offer.isEvent.is_(True),  # type: ignore [attr-defined]
            Offer.isDigital.is_(True),  # type: ignore [attr-defined]
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


def send_online_event_event_reminder_by_offer() -> None:
    bookings_query = _get_online_events_happening_tomorrow()
    email_data_by_stock = _get_email_data_by_stock(bookings_query)
    _send_email_by_stock(email_data_by_stock)


def cancel_online_event_reminder(booking_id: int) -> None:
    booking_message_id = app.redis_client.get(f"{booking_id}{constants.REDIS_SCHEDULED_EMAILS_SUFFIX}")
    if booking_message_id is None:
        return
    mails.cancel_scheduled_email(booking_message_id)
    app.redis_client.delete(f"{booking_id}{constants.REDIS_SCHEDULED_EMAILS_SUFFIX}")
