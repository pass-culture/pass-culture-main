from datetime import datetime
from typing import Dict

from models import Offer
from utils.human_ids import humanize


def build_object(offer: Offer) -> Dict:
    venue = offer.venue
    offerer = venue.managingOfferer
    humanize_offer_id = humanize(offer.id)
    has_coordinates = venue.latitude is not None and venue.longitude is not None
    date_range = list(map(str, offer.dateRange.datetimes))
    author = offer.extraData and offer.extraData.get('author')
    stage_director = offer.extraData and offer.extraData.get('stageDirector')
    visa = offer.extraData and offer.extraData.get('visa')
    isbn = offer.extraData and offer.extraData.get('isbn')
    speaker = offer.extraData and offer.extraData.get('speaker')
    performer = offer.extraData and offer.extraData.get('performer')
    show_type = offer.extraData and offer.extraData.get('showType')
    show_sub_type = offer.extraData and offer.extraData.get('showSubType')
    music_type = offer.extraData and offer.extraData.get('musicType')
    music_sub_type = offer.extraData and offer.extraData.get('musicSubType')
    price = offer.stocks and offer.stocks[0].price
    dates = []
    if offer.isEvent:
        stocks = offer.notDeletedStocks
        dates = list(map(lambda stock: datetime.timestamp(stock.beginningDatetime), stocks))
    date_created = datetime.timestamp(offer.dateCreated)

    object_to_index = {
        'objectID': humanize_offer_id,
        'offer': {
            'author': author,
            'dateCreated': date_created,
            'dateRange': date_range,
            'dates': dates,
            'description': offer.description,
            'id': humanize_offer_id,
            'isbn': isbn,
            'isDuo': offer.isDuo,
            'label': offer.offerType['appLabel'],
            'musicSubType': music_sub_type,
            'musicType': music_type,
            'name': offer.name,
            'performer': performer,
            'price': price,
            'showSubType': show_sub_type,
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
            'departementCode': venue.departementCode,
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
