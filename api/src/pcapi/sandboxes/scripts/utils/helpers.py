from datetime import datetime

from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.core.users.models import TokenType
from pcapi.routes.serialization import as_dict
from pcapi.utils.includes import USER_INCLUDES


def get_booking_helper(booking: bookings_models.Booking) -> dict:
    return dict(
        as_dict(booking),
        **{
            "eventOrThingName": booking.stock.offer.product.name,
            "venueName": booking.venue.name,
        },
    )


def get_offer_helper(offer: offers_models.Offer) -> dict:
    return dict(
        as_dict(offer),
        **{
            "venueCity": offer.venue.city,
            "venueName": offer.venue.name,
            "thingName": offer.product.name,
            "status": offer.status.name,  # type: ignore [attr-defined]
        },
    )


def get_offerer_helper(offerer: offerers_models.Offerer) -> dict:
    return dict(
        as_dict(offerer),
        **{
            "latitude": "48.9281995",
            "longitude": "2.4579903",
        },
    )


def get_stock_helper(stock: offers_models.Stock) -> dict:
    return as_dict(stock)


def get_email(first_name: str, last_name: str, domain: str) -> str:
    return "{}.{}@{}".format(
        first_name.replace(" ", "").strip().lower(), last_name.replace(" ", "").strip().lower(), domain
    )


def get_pro_helper(user: users_models.User) -> dict:
    return dict(
        as_dict(user, includes=USER_INCLUDES),
        **{
            "resetPasswordToken": _get_reset_password_token(user),
            "password": settings.TEST_DEFAULT_PASSWORD,
            "validationToken": user.validationToken,
        },
    )


def get_venue_helper(venue: offerers_models.Venue) -> dict:
    return as_dict(venue)


def _get_reset_password_token(user: users_models.User) -> str | None:
    for token in user.tokens:
        if token.type == TokenType.RESET_PASSWORD and token.expirationDate > datetime.utcnow():
            return token.value
    return None
