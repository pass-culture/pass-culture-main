from models import Offer
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_offer(offer_mock, event_or_thing=None, store=None):

    if 'eventKey' in offer_mock:
        if event_or_thing is None:
            event_or_thing = store['events_by_key'][offer_mock['eventKey']]
        is_event = True
        query = Offer.query.filter_by(eventId=event_or_thing.id)
    else:
        if event_or_thing is None:
            event_or_thing = store['things_by_key'][offer_mock['thingKey']]
        is_event = False
        query = Offer.query.filter_by(thingId=event_or_thing.id)
    venue = store['venues_by_key'][offer_mock['venueKey']]

    offer = query.filter_by(venueId=venue.id).first()

    if offer is None:
        offer = Offer(from_dict=offer_mock)
        if is_event:
            offer.event = event_or_thing
        else:
            offer.thing = event_or_thing
        # TODO: waiting for venue
        # offer.venue = venue
        offer.venueId = venue.id
        PcObject.check_and_save(offer)
        logger.info("created offer " + str(offer))
    else:
        logger.info('--already here-- offer' + str(offer))

    return offer

def create_or_find_offers(*offer_mocks, store=None):

    if store is None:
        store = {}

    offers_count = str(len(offer_mocks))
    logger.info("offer mocks " + offers_count)

    store['offers_by_key'] = {}

    for (offer_index, offer_mock) in enumerate(offer_mocks):
        if 'eventKey' in offer_mock:
            logger.info("look offer " + store['events_by_key'][offer_mock['eventKey']].name + " " + store['venues_by_key'][offer_mock['venueKey']].name+ " " + str(offer_index) + "/" + offers_count)
        else:
            logger.info("look offer " + store['things_by_key'][offer_mock['thingKey']].name + " " + store['venues_by_key'][offer_mock['venueKey']].name+ " " + str(offer_index) + "/" + offers_count)
        offer = create_or_find_offer(offer_mock, store=store)
        store['offers_by_key'][offer_mock['key']] = offer
