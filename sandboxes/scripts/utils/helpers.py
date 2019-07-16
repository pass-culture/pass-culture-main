from tests.test_utils import PLAIN_DEFAULT_TESTING_PASSWORD
from utils.includes import RECOMMENDATION_INCLUDES, USER_INCLUDES


def get_booking_helper(booking):
    return dict(booking.as_dict(), **{
        "eventOrThingName": booking.recommendation.offer.product.name,
        "venueName": booking.recommendation.offer.venue.name
    })


def get_mediation_helper(mediation):
    return mediation.as_dict()


def get_offer_helper(offer):
    return dict(offer.as_dict(), **{
        "keywordsString": '{} {}'.format(
            offer.product.name,
            offer.venue.name
        ).replace('?', ' ')
                .replace('!', ' ') \
                .replace('(', '') \
                .replace(')', '') \
                .replace('ù', 'u'),
        "venueCity": offer.venue.city,
        "venueName": offer.venue.name,
        "thingName": offer.product.name
    })


def get_offerer_helper(offerer):
    return dict(offerer.as_dict(), **{
        "keywordsString": offerer.name,
        "latitude": '48.9281995',
        "longitude": '2.4579903',
    })


def get_payment_helper(payment):
    return payment.as_dict()


def get_stock_helper(stock):
    return stock.as_dict()


def get_email(first_name, last_name, domain):
    return "{}.{}@{}".format(
        first_name.replace(' ', '').strip().lower(),
        last_name.replace(' ', '').strip().lower(),
        domain
    )


def get_user_helper(user):
    return dict(user.as_dict(include=USER_INCLUDES), **{
        "resetPasswordToken": user.resetPasswordToken,
        "password": PLAIN_DEFAULT_TESTING_PASSWORD,
        "validationToken": user.validationToken
    })


def get_venue_helper(venue):
    return venue.as_dict()


def get_recommendation_helper(recommendation):
    return recommendation.as_dict(include=RECOMMENDATION_INCLUDES)
