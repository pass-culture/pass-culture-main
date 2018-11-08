from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_venue

def create_grid_venues(offerers_by_name):
    logger.info('create_grid_venues')

    venue_by_name = {}
    for offerer in offerers_by_name.values():
        name = "LIEU " + str(offerer.siren)
        venue_by_name[name] = create_venue(
            offerer,
            address=offerer.address,
            booking_email="fake@email.com",
            city=offerer.city,
            comment="Pas de siret car je suis un mock.",
            latitude=offerer.address.split('lat:')[1],
            longitude=offerer.address.split('lon:')[1],
            name=name,
            postal_code=offerer.postalCode
        )

        digital_name = name + " Offre en ligne"
        venue_by_name[digital_name] = create_venue(
            offerer,
            is_virtual=True,
            name=name,
        )

    PcObject.check_and_save(*venue_by_name.values())

    return venue_by_name
