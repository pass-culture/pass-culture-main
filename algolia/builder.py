from typing import Dict

from models import Offer
from models.offer_type import ProductType
from utils.human_ids import humanize


def build_object(offer: Offer) -> Dict:
    venue = offer.venue
    offerer = venue.managingOfferer
    humanize_offer_id = humanize(offer.id)
    has_coordinates = venue.latitude is not None and venue.longitude is not None

    object_to_index = {
        'objectID': humanize_offer_id,
        'offer': {
            'author': '',
            'dateRange': offer.dateRange.datetimes,
            'description': offer.description,
            'id': humanize_offer_id,
            'label': offer.offerType['appLabel'],
            'name': offer.name,
            'thumbUrl': offer.product.thumbUrl,
            'type': offer.offerType['sublabel'],
        },
        'offerer': {
            'name': offerer.name,
        },
        'venue': {
            'city': venue.city,
            'name': venue.name,
            'publicName': venue.publicName
        }
    }

    if ProductType.is_book(str(offer.type)):
        object_to_index['offer']['author'] = offer.extraData['author']

    if has_coordinates:
        object_to_index.update({'_geoloc': {
            'lat': float(venue.latitude),
            'lng': float(venue.longitude)
        }})

    return object_to_index
