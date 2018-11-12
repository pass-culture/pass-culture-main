from domain.types import get_formatted_types_by_value
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_event_offer

def create_grid_event_offers(events_by_name, venues_by_name):
    logger.info('create_grid_event_offers')

    types_by_value = get_formatted_types_by_value()

    event_offers_by_name = {}

    venues = venues_by_name.values()

    for venue in venues:

        if venue.isVirtual:
            continue

        virtual_venue = [
            v for v in venues
            if venue.managingOffererId == v.managingOffererId
            and v.isVirtual
        ][0]

        for event in events_by_name.values():

            # DETERMINE THE MATCHING VENUE
            event_type = types_by_value[event.type]
            if event_type['offlineOnly']:
                event_venue = venue
            elif event_type['onlineOnly']:
                event_venue = virtual_venue
            else:
                event_venue = venue

            name = event.name + '/' + event_venue.name
            event_offers_by_name[name] = create_event_offer(
                event_venue,
                event=event,
                event_type=event.type
            )

    PcObject.check_and_save(*event_offers_by_name.values())

    return event_offers_by_name
