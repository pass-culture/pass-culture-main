import datetime

from babel.dates import format_date

from pcapi.models import Booking
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import get_event_datetime


def retrieve_data_to_warn_user_after_pro_booking_cancellation(booking: Booking) -> dict:
    stock = booking.stock
    offer = stock.offer
    event_date = ""
    event_hour = ""
    is_event = int(offer.isEvent)
    if is_event:
        event_date = format_date(get_event_datetime(stock), format="full", locale="fr")
        event_hour = format_booking_hours_for_email(booking)
    is_free_offer = 1 if stock.price == 0 else 0
    is_thing = int(offer.isThing)
    is_online = int(offer.isDigital)
    if is_online:
        is_event = 0
        is_thing = 0
    offerer_name = offer.venue.managingOfferer.name
    offer_name = offer.name
    offer_price = str(booking.total_amount)
    user_first_name = booking.individualBooking.user.firstName
    venue_name = offer.venue.publicName if offer.venue.publicName else offer.venue.name
    can_book_again = int(booking.user.deposit.expirationDate > datetime.datetime.now())

    return {
        "MJ-TemplateID": 1116690,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "event_date": event_date,
            "event_hour": event_hour,
            "is_event": is_event,
            "is_free_offer": is_free_offer,
            "is_online": is_online,
            "is_thing": is_thing,
            "offer_name": offer_name,
            "offer_price": offer_price,
            "offerer_name": offerer_name,
            "user_first_name": user_first_name,
            "can_book_again": can_book_again,
            "venue_name": venue_name,
        },
    }
