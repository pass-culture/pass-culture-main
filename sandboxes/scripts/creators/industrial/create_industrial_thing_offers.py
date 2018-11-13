from domain.types import get_formatted_event_or_thing_types_by_value
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing_offer

def create_industrial_thing_offers(
    things_by_name,
    venues_by_name,
    offerers_by_name
):
    logger.info('create_industrial_thing_offers')

    types_by_value = get_formatted_event_or_thing_types_by_value()

    thing_offers_by_name = {}

    for offerer_name in offerers_by_name.keys():

        venue = venues_by_name[offerer_name]

        virtual_venue = venues_by_name[offerer_name + " (Offre en ligne)"]

        for thing in things_by_name.values():

            # DETERMINE THE MATCHING VENUE
            thing_type = types_by_value[thing.type]
            if thing_type['offlineOnly']:
                thing_venue = venue
            elif thing_type['onlineOnly']:
                thing_venue = virtual_venue
            else:
                thing_venue = venue

            name = thing.name + ' / ' + thing_venue.name
            thing_offers_by_name[name] = create_thing_offer(
                thing_venue,
                thing=thing,
                thing_type=thing.type
            )

    PcObject.check_and_save(*thing_offers_by_name.values())

    return thing_offers_by_name
