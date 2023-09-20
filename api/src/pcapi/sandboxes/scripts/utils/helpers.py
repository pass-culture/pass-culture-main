from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
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
    resetPasswodToken = _get_reset_password_token(user)
    if not resetPasswodToken:
        raise users_exceptions.InvalidToken("No reset password token found")
    return dict(
        as_dict(user, includes=USER_INCLUDES),
        **{
            "resetPasswordToken": resetPasswodToken.encoded_token,
            "password": settings.TEST_DEFAULT_PASSWORD,
            "validationToken": user.validationToken,
        },
    )


def get_venue_helper(venue: offerers_models.Venue) -> dict:
    return as_dict(venue)


def _get_reset_password_token(user: users_models.User) -> token_utils.Token | None:
    return token_utils.Token.get_token(token_utils.TokenType.RESET_PASSWORD, user.id)
