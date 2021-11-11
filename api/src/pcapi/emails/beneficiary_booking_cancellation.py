import datetime

from pcapi.core.bookings.models import IndividualBooking
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.human_ids import humanize


def make_beneficiary_booking_cancellation_email_data(individual_booking: IndividualBooking) -> dict:
    stock = individual_booking.booking.stock
    beneficiary = individual_booking.user
    offer = stock.offer
    event_date = ""
    event_hour = ""
    first_name = beneficiary.firstName
    is_event = int(offer.isEvent)
    offer_id = humanize(offer.id)
    offer_name = offer.name
    price = str(individual_booking.booking.total_amount)
    is_free_offer = 1 if stock.price == 0 else 0
    can_book_again = int(beneficiary.deposit.expirationDate > datetime.datetime.now())

    if is_event:
        beginning_date_time_in_tz = utc_datetime_to_department_timezone(
            stock.beginningDatetime, offer.venue.departementCode
        )
        event_date = get_date_formatted_for_email(beginning_date_time_in_tz)
        event_hour = get_time_formatted_for_email(beginning_date_time_in_tz)

    return {
        "Mj-TemplateID": 1091464,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "event_date": event_date,
            "event_hour": event_hour,
            "is_free_offer": is_free_offer,
            "is_event": is_event,
            "offer_id": offer_id,
            "offer_name": offer_name,
            "offer_price": price,
            "user_first_name": first_name,
            "can_book_again": can_book_again,
        },
    }
