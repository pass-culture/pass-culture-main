from babel.dates import format_date

from pcapi.models import Booking
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import get_event_datetime


def retrieve_data_to_warn_user_after_stock_update_affecting_booking(booking: Booking) -> dict:
    stock = booking.stock
    offer = stock.offer
    offer_name = offer.name
    user_first_name = booking.firstName
    venue_name = offer.venue.publicName if offer.venue.publicName else offer.venue.name
    is_event = int(offer.isEvent)
    event_date = ""
    event_hour = ""
    if is_event:
        event_date = format_date(get_event_datetime(stock), format="full", locale="fr")
        event_hour = format_booking_hours_for_email(booking)

    return {
        "MJ-TemplateID": 1332139,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "offer_name": offer_name,
            "user_first_name": user_first_name,
            "venue_name": venue_name,
            "event_date": event_date,
            "event_hour": event_hour,
        },
    }
