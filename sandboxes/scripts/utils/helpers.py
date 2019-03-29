def get_booking_helper(booking):
    return dict(booking._asdict(), **{
        "eventOrThingName": booking.recommendation.offer.eventOrThing.name,
        "venueName": booking.recommendation.offer.venue.name
    })

def get_mediation_helper(mediation):
    return mediation._asdict()

def get_offer_helper(offer):
    return dict(offer._asdict(), **{
        "keywordsString": '{} {}'.format(
            offer.eventOrThing.name,
            offer.venue.name
        ).replace('?', ' ') \
         .replace('!', ' ') \
         .replace('(', '') \
         .replace(')', '') \
         .replace('ù', 'u'),
        "venueCity": offer.venue.city,
        "venueName": offer.venue.name,
        "thingName": offer.eventOrThing.name
    })

def get_offerer_helper(offerer):
    return dict(offerer._asdict(), **{
        "keywordsString": offerer.name,
        "latitude": '48.9281995',
        "longitude": '2.4579903',
    })

def get_stock_helper(stock):
    return stock._asdict()

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
    return dict(user._asdict(), **{
        "password": get_password_from_email(user.email)
    })

def get_venue_helper(venue):
    return venue._asdict()
