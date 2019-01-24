from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing_offer

THINGS_COUNT_PER_VENUE = 2

def create_industrial_thing_offers(
        things_by_name,
        venues_by_name,
        offerers_by_name
):
    logger.info('create_industrial_thing_offers')

    thing_offers_by_name = {}

    id_at_providers = 1234

    thing_index = 0
    thing_items = list(things_by_name.items())

    for offerer in offerers_by_name.values():

        virtual_venues = [
            venue for venue in offerer.managedVenues
            if venue.isVirtual
        ]
        for virtual_venue in virtual_venues:

            physical_venue_name = virtual_venue.name.replace(" (Offre en ligne)", "")
            physical_venue = venues_by_name.get(physical_venue_name)

            for venue_thing_index in range(0, THINGS_COUNT_PER_VENUE):

                (thing_name, thing) = thing_items[thing_index + venue_thing_index]

                thing_venue = None
                if thing.offerType['offlineOnly']:
                    thing_venue = physical_venue
                elif thing.offerType['onlineOnly']:
                    thing_venue = virtual_venue
                else:
                    thing_venue = physical_venue

                if thing_venue is None:
                    continue

                name = "{} / {}".format(thing_name, thing_venue.name)
                thing_offers_by_name[name] = create_thing_offer(
                    thing_venue,
                    thing=thing,
                    thing_type=thing.type,
                    id_at_providers=id_at_providers
                )

                id_at_providers += 1

            thing_index += THINGS_COUNT_PER_VENUE

    PcObject.check_and_save(*thing_offers_by_name.values())

    logger.info('created {} thing_offers'.format(len(thing_offers_by_name)))

    return thing_offers_by_name
