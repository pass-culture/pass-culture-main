from utils.includes import RECOMMENDATION_INCLUDES

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

def get_password_from_email(email):
    chunks = email.split('.')

    first_chunk_with_at_least_one_number = chunks[0].lower()
    if not first_chunk_with_at_least_one_number[-1].isdigit():
        first_chunk_with_at_least_one_number += '0'

    second_chunk_with_at_least_one_capital_letter = ".".join(
        [chunks[1].capitalize()] + chunks[2:]
    ).split('@')[0]

    minimal_password = "{}.{}".format(
        first_chunk_with_at_least_one_number,
        second_chunk_with_at_least_one_capital_letter
    )
    if len(minimal_password) < 8:
        minimal_password += ''.join(['x'])*(8-len(minimal_password))
    return minimal_password

def get_user_helper(user):
    return dict(user.as_dict(), **{
        "password": get_password_from_email(user.email)
    })

def get_venue_helper(venue):
    return venue.as_dict()

def get_recommendation_helper(recommendation):
    return recommendation.as_dict(include=RECOMMENDATION_INCLUDES)
