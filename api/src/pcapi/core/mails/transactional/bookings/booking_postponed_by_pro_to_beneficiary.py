from babel.dates import format_date

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import get_event_datetime
from pcapi.utils.urls import booking_app_link


def send_batch_booking_postponement_email_to_users(bookings: list[Booking]) -> bool:
    success = True
    for booking in bookings:
        success &= send_booking_postponement_email_to_users(booking)
    return success


def send_booking_postponement_email_to_users(booking: Booking) -> bool:
    data = get_booking_postponed_by_pro_to_beneficiary_email_data(booking)
    return mails.send(recipients=[booking.email], data=data)  # type: ignore [list-item]


def get_booking_postponed_by_pro_to_beneficiary_email_data(
    booking: Booking,
) -> models.TransactionalEmailData:
    stock = booking.stock
    offer = stock.offer

    if offer.isEvent:
        event_date = format_date(get_event_datetime(stock), format="full", locale="fr")
        event_hour = format_booking_hours_for_email(booking)
    else:
        event_date = None
        event_hour = None

    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value,
        params={
            "OFFER_NAME": offer.name,
            "FIRSTNAME": booking.firstName,
            "IS_EXTERNAL": booking.isExternal,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "EVENT_DATE": event_date if event_date else "",
            "EVENT_HOUR": event_hour if event_hour else "",
            "BOOKING_LINK": booking_app_link(booking),
        },
    )
