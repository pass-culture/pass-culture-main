from pcapi.core.users.models import User
from pcapi.models import Booking
from pcapi.models.feature import FeatureToggle


OLD_MAILJET_TEMPLATE_ID = 1951103
NEW_MAILJET_TEMPLATE_ID = 3095107


def build_expired_bookings_recap_email_data_for_beneficiary(
    beneficiary: User, bookings: list[Booking], withdrawal_period: int
) -> dict:
    mj_template_id = (
        NEW_MAILJET_TEMPLATE_ID
        if FeatureToggle.ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS.is_active()
        else OLD_MAILJET_TEMPLATE_ID
    )
    return {
        "Mj-TemplateID": mj_template_id,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "user_firstName": beneficiary.firstName,
            "bookings": _extract_bookings_information_from_bookings_list(bookings),
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
            }
        )
    return bookings_info
