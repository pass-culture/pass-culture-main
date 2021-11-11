from pcapi.models import Booking
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(bookings: list[Booking]) -> dict:
    booking = bookings[0]
    stock = booking.stock
    offer = stock.offer
    event_date = format_booking_date_for_email(booking)
    event_hour = format_booking_hours_for_email(booking)
    offer_link = build_pc_pro_offer_link(offer)
    offer_price = str(stock.price) if stock.price > 0 else "Gratuit"
    quantity = sum([booking.quantity for booking in bookings])
    venue_name = offer.venue.publicName if offer.venue.publicName else offer.venue.name

    return {
        "MJ-TemplateID": 1116333,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "offer_name": offer.name,
            "venue_name": venue_name,
            "price": offer_price,
            "is_event": int(offer.isEvent),
            "event_date": event_date,
            "event_hour": event_hour,
            "quantity": quantity,
            "reservations_number": len(bookings),
            "lien_offre_pcpro": offer_link,
            "users": _extract_users_information_from_bookings_list(bookings),
        },
    }


def _extract_users_information_from_bookings_list(bookings: list[Booking]) -> list[dict]:
    users_keys = ("firstName", "lastName", "email", "countermark")
    users_properties = [[booking.firstName, booking.lastName, booking.email, booking.token] for booking in bookings]

    return [dict(zip(users_keys, user_property)) for user_property in users_properties]
