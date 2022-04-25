from datetime import datetime

from pcapi import settings
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.routes.serialization import as_dict
from pcapi.utils.includes import USER_INCLUDES


def get_booking_helper(booking):  # type: ignore [no-untyped-def]
    return dict(
        as_dict(booking),
        **{
            "eventOrThingName": booking.stock.offer.product.name,
            "venueName": booking.venue.name,
        },
    )


def get_offer_helper(offer):  # type: ignore [no-untyped-def]
    return dict(
        as_dict(offer),
        **{
            "venueCity": offer.venue.city,
            "venueName": offer.venue.name,
            "thingName": offer.product.name,
            "status": offer.status.name,
        },
    )


def get_offerer_helper(offerer):  # type: ignore [no-untyped-def]
    return dict(
        as_dict(offerer),
        **{
            "latitude": "48.9281995",
            "longitude": "2.4579903",
        },
    )


def get_stock_helper(stock):  # type: ignore [no-untyped-def]
    return as_dict(stock)


def get_email(first_name, last_name, domain):  # type: ignore [no-untyped-def]
    return "{}.{}@{}".format(
        first_name.replace(" ", "").strip().lower(), last_name.replace(" ", "").strip().lower(), domain
    )


def get_pro_helper(user):  # type: ignore [no-untyped-def]
    return dict(
        as_dict(user, includes=USER_INCLUDES),
        **{
            "resetPasswordToken": _get_reset_password_token(user),
            "password": settings.TEST_DEFAULT_PASSWORD,
            "validationToken": user.validationToken,
        },
    )


def get_venue_helper(venue):  # type: ignore [no-untyped-def]
    return as_dict(venue)


def _get_reset_password_token(user: User):  # type: ignore [no-untyped-def]
    for token in user.tokens:
        if token.type == TokenType.RESET_PASSWORD and token.expirationDate > datetime.utcnow():
            return token.value
    return None
