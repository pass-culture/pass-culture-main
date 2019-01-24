from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_event_offer

EVENTS_COUNT_PER_VENUE = 2

def create_industrial_event_offers(
        events_by_name,
        venues_by_name,
        offerers_by_name
):
    logger.info('create_industrial_event_offers')

    event_offers_by_name = {}

    event_index = 0
    event_items = list(events_by_name.items())

    for offerer in offerers_by_name.values():

        virtual_venues = [
            venue for venue in offerer.managedVenues
            if venue.isVirtual
        ]
        for virtual_venue in virtual_venues:

            physical_venue_name = virtual_venue.name.replace(" (Offre en ligne)", "")
            physical_venue = venues_by_name.get(physical_venue_name)

            for venue_event_index in range(0, EVENTS_COUNT_PER_VENUE):

                (event_name, event) = event_items[venue_event_index + event_index]

                event_venue = None
                if event.offerType['offlineOnly']:
                    event_venue = physical_venue
                elif event.offerType['onlineOnly']:
                    event_venue = virtual_venue
                else:
                    event_venue = physical_venue

                if event_venue is None:
                    continue

                name = "{} / {}".format(event_name, event_venue.name)
                event_offers_by_name[name] = create_event_offer(
                    event_venue,
                    event=event,
                    event_type=event.type
                )

            event_index += EVENTS_COUNT_PER_VENUE



    PcObject.check_and_save(*event_offers_by_name.values())

    logger.info('created {} event_offers'.format(len(event_offers_by_name)))

    return event_offers_by_name
