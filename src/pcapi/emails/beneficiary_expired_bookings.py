import typing

from pcapi import settings
from pcapi.core.users.models import User
from pcapi.models import Booking
from pcapi.repository.feature_queries import feature_send_mail_to_users_enabled
from pcapi.utils.mailing import format_environment_for_email


def build_expired_bookings_recap_email_data_for_beneficiary(
    beneficiary: User, bookings: typing.List[Booking]
) -> typing.Dict:
    return {
        "FromEmail": settings.SUPPORT_EMAIL_ADDRESS
        if feature_send_mail_to_users_enabled()
        else settings.DEV_EMAIL_ADDRESS,
        "Mj-TemplateID": 1951103,
        "Mj-TemplateLanguage": True,
        "To": beneficiary.email if feature_send_mail_to_users_enabled() else settings.DEV_EMAIL_ADDRESS,
        "Vars": {
            "user_firstName": beneficiary.firstName,
            "bookings": _extract_bookings_information_from_bookings_list(bookings),
            "env": format_environment_for_email(),
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
