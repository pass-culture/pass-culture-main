from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Stock
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


def get_reminder_7_days_before_event_email_data(stock: Stock) -> models.TransactionalEmailData:
    event_datetime = get_event_datetime(stock)
    return models.TransactionalEmailData(
        template=TransactionalEmail.REMINDER_7_DAYS_BEFORE_EVENT_TO_PRO.value,
        params={
            "OFFER_NAME": stock.offer.name,
            "VENUE_NAME": stock.offer.venue.common_name,
            "EVENT_DATE": get_date_formatted_for_email(event_datetime),
            "EVENT_HOUR": get_time_formatted_for_email(event_datetime),
            "BOOKING_COUNT": stock.dnBookedQuantity,
            "OFFER_ADDRESS": stock.offer.fullAddress,
        },
    )


def send_reminder_7_days_before_event_to_pro(stock: Stock) -> None:
    recipient = stock.offer.bookingEmail or stock.offer.venue.bookingEmail
    if not recipient:
        return
    data = get_reminder_7_days_before_event_email_data(stock)
    mails.send(recipients=[recipient], data=data)
