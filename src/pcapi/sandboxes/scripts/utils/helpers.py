from datetime import datetime

from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.routes.serialization import as_dict
from pcapi.utils.includes import BENEFICIARY_INCLUDES
from pcapi.utils.includes import USER_INCLUDES


def get_booking_helper(booking):
    return dict(
        as_dict(booking),
        **{
            "eventOrThingName": booking.stock.offer.product.name,
            "venueName": booking.stock.offer.venue.name,
        },
    )


def get_mediation_helper(mediation):
    return as_dict(mediation)


def get_offer_helper(offer):
    return dict(
        as_dict(offer),
        **{
            "venueCity": offer.venue.city,
            "venueName": offer.venue.name,
            "thingName": offer.product.name,
            "status": offer.status.name,
        },
    )


def get_offerer_helper(offerer):
    return dict(
        as_dict(offerer),
        **{
            "latitude": "48.9281995",
            "longitude": "2.4579903",
        },
    )


def get_payment_helper(payment):
    return as_dict(payment)


def get_stock_helper(stock):
    return as_dict(stock)


def get_email(first_name, last_name, domain):
    return "{}.{}@{}".format(
        first_name.replace(" ", "").strip().lower(), last_name.replace(" ", "").strip().lower(), domain
    )


def get_pro_helper(user):
    return dict(
        as_dict(user, includes=USER_INCLUDES),
        **{
            "resetPasswordToken": _get_reset_password_token(user),
            "password": users_factories.DEFAULT_PASSWORD,
            "validationToken": user.validationToken,
        },
    )


def get_beneficiary_helper(user):
    return dict(
        as_dict(user, includes=BENEFICIARY_INCLUDES),
        **{
            "resetPasswordToken": _get_reset_password_token(user),
            "password": users_factories.DEFAULT_PASSWORD,
            "validationToken": user.validationToken,
        },
    )


def get_venue_helper(venue):
    return as_dict(venue)


def _get_reset_password_token(user: User):
    for token in user.tokens:
        if token.type == TokenType.RESET_PASSWORD and token.expirationDate > datetime.now():
            return token.value
    return None
