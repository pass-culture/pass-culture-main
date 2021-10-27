from pcapi.core.offerers.models import Offerer
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import Booking
from pcapi.utils.mailing import build_pc_pro_offer_link


def build_expired_bookings_recap_email_data_for_offerer(
    offerer: Offerer, bookings: list[Booking], withdrawal_period
) -> dict:
    return {
        "Mj-TemplateID": 3095184,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "bookings": _extract_bookings_information_from_bookings_list(bookings),
            "department": PostalCode(offerer.postalCode).get_departement_code(),
            "withdrawal_period": withdrawal_period,
        },
    }


def _extract_bookings_information_from_bookings_list(bookings: list[Booking]) -> list[dict]:
    bookings_info = []
    for booking in bookings:
        stock = booking.stock
        offer = stock.offer
        bookings_info.append(
            {
                "offer_name": offer.name,
                "venue_name": offer.venue.publicName if offer.venue.publicName else offer.venue.name,
                "price": str(stock.price) if stock.price > 0 else "gratuit",
                "user_name": booking.publicName,
                "user_email": booking.email,
                "pcpro_offer_link": build_pc_pro_offer_link(offer),
            }
        )
    return bookings_info
