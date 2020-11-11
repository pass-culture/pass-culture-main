from pcapi.model_creators.generic_creators import PLAIN_DEFAULT_TESTING_PASSWORD
from pcapi.routes.serialization import as_dict
from pcapi.utils.includes import BENEFICIARY_INCLUDES
from pcapi.utils.includes import RECOMMENDATION_INCLUDES
from pcapi.utils.includes import USER_INCLUDES


def get_booking_helper(booking):
    return dict(
        as_dict(booking),
        **{
            "eventOrThingName": booking.recommendation.offer.product.name,
            "venueName": booking.recommendation.offer.venue.name,
        },
    )


def get_mediation_helper(mediation):
    return as_dict(mediation)


def get_offer_helper(offer):
    return dict(
        as_dict(offer),
        **{
            "keywordsString": "{}".format(offer.product.name)
            .replace("?", " ")
            .replace("!", " ")
            .replace("(", "")
            .replace(")", "")
            .replace("ù", "u"),
            "venueCity": offer.venue.city,
            "venueName": offer.venue.name,
            "thingName": offer.product.name,
        },
    )


def get_offerer_helper(offerer):
    return dict(
        as_dict(offerer),
        **{
            "keywordsString": offerer.name,
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
            "resetPasswordToken": user.resetPasswordToken,
            "password": PLAIN_DEFAULT_TESTING_PASSWORD,
            "validationToken": user.validationToken,
        },
    )


def get_beneficiary_helper(user):
    return dict(
        as_dict(user, includes=BENEFICIARY_INCLUDES),
        **{
            "resetPasswordToken": user.resetPasswordToken,
            "password": PLAIN_DEFAULT_TESTING_PASSWORD,
            "validationToken": user.validationToken,
        },
    )


def get_venue_helper(venue):
    return as_dict(venue)


def get_recommendation_helper(recommendation):
    return as_dict(recommendation, includes=RECOMMENDATION_INCLUDES)
