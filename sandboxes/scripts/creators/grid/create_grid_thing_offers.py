from domain.types import get_formatted_types_by_value
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing_offer

def create_grid_thing_offers(things_by_name, venues_by_name):
    logger.info('create_grid_thing_offers')

    types_by_value = get_formatted_types_by_value()

    thing_offers_by_name = {}

    venues = venues_by_name.values()

    for venue in venues:

        if venue.isVirtual:
            continue

        virtual_venue = [
            v for v in venues
            if venue.managingOffererId == v.managingOffererId
            and v.isVirtual
        ][0]

        for thing in things_by_name.values():

            # DETERMINE THE MATCHING VENUE
            thing_type = types_by_value[thing.type]
            if thing_type['offlineOnly']:
                thing_venue = venue
            elif thing_type['onlineOnly']:
                thing_venue = virtual_venue
            else:
                thing_venue = venue

            name = thing.name + '/' + thing_venue.name
            thing_offers_by_name[name] = create_thing_offer(
                thing_venue,
                thing=thing,
                thing_type=thing.type
            )

    PcObject.check_and_save(*thing_offers_by_name.values())

    return thing_offers_by_name
