import os
import typing

from pcapi.models import Booking
from pcapi.models import UserSQLEntity
from pcapi.repository.feature_queries import feature_send_mail_to_users_enabled
from pcapi.utils.mailing import DEV_EMAIL_ADDRESS


SUPPORT_EMAIL_ADDRESS = os.environ.get("SUPPORT_EMAIL_ADDRESS")


def build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary(
    beneficiary: UserSQLEntity, bookings: typing.List[Booking]
) -> typing.Dict:
    return {
        "FromEmail": SUPPORT_EMAIL_ADDRESS if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        "Mj-TemplateID": 1927224,
        "Mj-TemplateLanguage": True,
        "To": beneficiary.email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        "Vars": {
            "user_firstName": beneficiary.firstName,
            "bookings": _extract_bookings_information_from_bookings_list(bookings),
        },
    }


def _extract_bookings_information_from_bookings_list(bookings: typing.List[Booking]) -> typing.List[dict]:
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
