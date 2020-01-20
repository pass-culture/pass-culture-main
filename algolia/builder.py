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
    isbn = offer.extraData and offer.extraData.get('isbn')
    speaker = offer.extraData and offer.extraData.get('speaker')
    performer = offer.extraData and offer.extraData.get('performer')
    show_type = offer.extraData and offer.extraData.get('showType')
    music_type = offer.extraData and offer.extraData.get('musicType')

    object_to_index = {
        'objectID': humanize_offer_id,
        'offer': {
            'author': author,
            'dateRange': list(date_range),
            'description': offer.description,
            'id': humanize_offer_id,
            'isbn': isbn,
            'label': offer.offerType['appLabel'],
            'musicType': music_type,
            'name': offer.name,
            'performer': performer,
            'showType': show_type,
            'speaker': speaker,
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
