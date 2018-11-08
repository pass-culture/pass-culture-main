from domain.types import get_types_by_value
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_event_offer

def create_grid_event_offers(events_by_name, venues_by_name):

    types_by_value = get_types_by_value()

    event_offers_by_name = {}

    venues = venues_by_name.values()

    for venue in venues:

        if venue.isVirtual:
            continue

        virtual_venue_mock = [
            vm for vm in venues
            if venue.managingOffererId == v.managingOffererId
            and v.isVirtual
        ][0]

        for event in events_by_name.values():

            # DETERMINE THE MATCHING VENUE
            event_type = types_by_value[event_mock['type']]
            if event_type['offlineOnly']:
                thing_venue = venue
            elif event_type['onlineOnly']:
                thing_venue = virtual_venue
            else:
                thing_venue = venue

            offer_mock = create_event_offer(thing_venue,
                event=event,
                is_active=True,
                type=event.type
            )

    PcObject.check_and_save(*event_offers_by_name.values())

    return offer_mocks
