from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing_offer

def create_industrial_thing_offers(
        things_by_name,
        venues_by_name,
        offerers_by_name
):
    logger.info('create_industrial_thing_offers')

    thing_offers_by_name = {}

    id_at_providers = 1234

    for offerer in offerers_by_name.values():

        physical_venues = [
            venue for venue in offerer.managedVenues
            if not venue.isVirtual
        ]
        for physical_venue in physical_venues:

            virtual_venue = venues_by_name[physical_venue.name + " (Offre en ligne)"]

            for (thing_name, thing) in things_by_name.items():

                if thing.offerType['offlineOnly']:
                    thing_venue = physical_venue
                elif thing.offerType['onlineOnly']:
                    thing_venue = virtual_venue
                else:
                    thing_venue = physical_venue

                name = "{} / {}".format(thing_name, thing_venue.name)
                thing_offers_by_name[name] = create_thing_offer(
                    thing_venue,
                    thing=thing,
                    thing_type=thing.type,
                    id_at_providers=id_at_providers
                )

                id_at_providers += 1

    PcObject.check_and_save(*thing_offers_by_name.values())

    logger.info('created {} thing_offers'.format(len(thing_offers_by_name)))

    return thing_offers_by_name
