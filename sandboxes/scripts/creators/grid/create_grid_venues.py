import re

from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_venue

def create_grid_venues(offerers_by_name):
    logger.info('create_grid_venues')

    venue_by_name = {}
    for offerer in offerers_by_name.values():
        name = "LIEU " + str(offerer.siren)
        geoloc_match = re.match(r'(.*)lat\:(.*) lon\:(.*)', offerer.address)
        venue_by_name[name] = create_venue(
            offerer,
            address=offerer.address,
            booking_email="fake@email.com",
            city=offerer.city,
            comment="Pas de siret car je suis un mock.",
            latitude=float(geoloc_match.group(2)),
            longitude=float(geoloc_match.group(3)),
            name=name,
            postal_code=offerer.postalCode,
            siret=None
        )

        digital_name = name + " Offre en ligne"
        venue_by_name[digital_name] = create_venue(
            offerer,
            is_virtual=True,
            name=name,
            siret=None
        )

    PcObject.check_and_save(*venue_by_name.values())

    return venue_by_name
