from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime
from pcapi.utils.urls import booking_app_link


def send_batch_booking_postponement_email_to_users(bookings: list[Booking]) -> None:
    for booking in bookings:
        send_booking_postponement_email_to_users(booking)


def send_booking_postponement_email_to_users(booking: Booking) -> None:
    data = get_booking_postponed_by_pro_to_beneficiary_email_data(booking)
    mails.send(recipients=[booking.email], data=data)


def get_booking_postponed_by_pro_to_beneficiary_email_data(
    booking: Booking,
) -> models.TransactionalEmailData:
    stock = booking.stock
    offer = stock.offer

    if offer.isEvent:
        event_date = get_date_formatted_for_email(get_event_datetime(stock)) if stock.beginningDatetime else ""
        event_hour = get_time_formatted_for_email(get_event_datetime(stock)) if stock.beginningDatetime else ""
    else:
        event_date = ""
        event_hour = ""

    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value,
        params={
            "OFFER_NAME": offer.name,
            "FIRSTNAME": booking.firstName,
            "IS_EXTERNAL": booking.isExternal,
            "VENUE_NAME": offer.venue.common_name,
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "BOOKING_LINK": booking_app_link(booking),
        },
    )
