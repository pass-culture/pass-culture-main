from models import Event, Offer, Thing, Venue
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_offer(offer_mock, event_or_thing=None):

    if 'eventId' in offer_mock:
        if event_or_thing is None:
            event_or_thing = Event.query.get(dehumanize(offer_mock['eventId']))
        is_event = True
        query = Offer.query.filter_by(eventId=event_or_thing.id)
    else:
        if event_or_thing is None:
            event_or_thing = Thing.query.get(dehumanize(offer_mock['thingId']))
        is_event = False
        query = Offer.query.filter_by(thingId=event_or_thing.id)
    venue = Venue.query.get(dehumanize(offer_mock['venueId']))

    logger.info("look offer " + event_or_thing.name + " " + venue.name + " " + offer_mock.get('id'))

    offer = query.filter_by(venueId=venue.id).first()

    if offer is None:
        offer = Offer(from_dict=offer_mock)
        if is_event:
            offer.event = event_or_thing
        else:
            offer.thing = event_or_thing
        offer.venue = venue
        if 'id' in offer_mock:
            offer.id = dehumanize(offer_mock['id'])
        PcObject.check_and_save(offer)
        logger.info("created offer " + str(offer))
    else:
        logger.info('--already here-- offer' + str(offer))

    return offer

def create_or_find_offers(*offer_mocks):
    offers_count = str(len(offer_mocks))
    logger.info("offer mocks " + offers_count)

    offers = []
    for (offer_index, offer_mock) in enumerate(offer_mocks):
        logger.info(str(offer_index) + "/" + offers_count)
        offer = create_or_find_offer(offer_mock)
        offers.append(offer)

    return offers
