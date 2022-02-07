from typing import Union

from babel.dates import format_date

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.models.feature import FeatureToggle
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import get_event_datetime
from pcapi.utils.urls import booking_app_link


def send_batch_booking_postponement_email_to_users(bookings: list[Booking]) -> list[bool]:
    success = True
    for booking in bookings:
        success &= send_booking_postponement_email_to_users(booking)
    return success


def send_booking_postponement_email_to_users(booking: Booking) -> bool:
    data = get_booking_postponed_by_pro_to_beneficiary_email_data(booking)
    return mails.send(recipients=[booking.email], data=data)


def get_booking_postponed_by_pro_to_beneficiary_email_data(
    booking: Booking,
) -> Union[dict, SendinblueTransactionalEmailData]:
    stock = booking.stock
    offer = stock.offer

    if offer.isEvent:
        event_date = format_date(get_event_datetime(stock), format="full", locale="fr")
        event_hour = format_booking_hours_for_email(booking)
    else:
        event_date = None
        event_hour = None

    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "MJ-TemplateID": 1332139,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "offer_name": offer.name,
                "user_first_name": booking.firstName,
                "venue_name": offer.venue.publicName or offer.venue.name,
                "event_date": event_date if event_date else "",
                "event_hour": event_hour if event_hour else "",
                "booking_link": booking_app_link(booking),
            },
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY.value,
        params={
            "OFFER_NAME": offer.name,
            "FIRSTNAME": booking.firstName,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "EVENT_DATE": event_date if event_date else "",
            "EVENT_HOUR": event_hour if event_hour else "",
            "BOOKING_LINK": booking_app_link(booking),
        },
    )
