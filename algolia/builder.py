from typing import Dict

from models import Offer
from utils.human_ids import humanize


def build_object(offer: Offer) -> Dict:
    venue = offer.venue
    offerer = venue.managingOfferer
    humanize_offer_id = humanize(offer.id)
    has_coordinates = venue.latitude is not None and venue.longitude is not None
    date_range = map(str, offer.dateRange.datetimes)
    author = offer.extraData and offer.extraData.get('author')
    stage_director = offer.extraData and offer.extraData.get('stageDirector')
    visa = offer.extraData and offer.extraData.get('visa')

    object_to_index = {
        'objectID': humanize_offer_id,
        'offer': {
            'author': author,
            'dateRange': list(date_range),
            'description': offer.description,
            'id': humanize_offer_id,
            'label': offer.offerType['appLabel'],
            'name': offer.name,
            'stageDirector': stage_director,
            'thumbUrl': offer.thumb_url,
            'type': offer.offerType['sublabel'],
            'visa': visa,
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

    if has_coordinates:
        object_to_index.update({'_geoloc': {
            'lat': float(venue.latitude),
            'lng': float(venue.longitude)
        }})

    return object_to_index
