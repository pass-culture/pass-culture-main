from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_venue

def create_scratch_venues(offerers_by_name):
    logger.info('create_scratch_venues')

    venues_by_name = {}

    offerer = offerers_by_name['LE GRAND REX PARIS']
    name = "LIEU " + str(offerer.siren)
    venues_by_name['LE GRAND REX PARIS'] = create_venue(
        offerer,
        address=offerer.address,
        booking_email="fake@email.com",
        city=offerer.city,
        latitude=48.870665,
        longitude=2.3478,
        name=name,
        postal_code=offerer.postalCode,
        siret=offerer.siren + "00016"
    )

    digital_name = name + " Offre en ligne"
    venues_by_name['LE GRAND REX PARIS (ON)'] = create_venue(
        offerer,
        is_virtual=True,
        name=digital_name,
        siret=None
    )

    offerer = offerers_by_name["THEATRE DE L ODEON"]
    name = "LIEU " + str(offerer.siren)
    venues_by_name["THEATRE DE L ODEON"] = create_venue(
        offerer,
        address=offerer.address,
        booking_email="fake2@email.com",
        city=offerer.city,
        latitude=45.762606,
        longitude=4.836694,
        name=name,
        postal_code=offerer.postalCode,
        siret=offerer.siren + "00025"
    )

    digital_name = name + " Offre en ligne"
    venues_by_name['THEATRE DE L ODEON (ON)'] = create_venue(
        offerer,
        is_virtual=True,
        name=digital_name,
        siret=None
    )

    offerer = offerers_by_name["THEATRE DU SOLEIL"]
    name = "LIEU " + str(offerer.siren)
    digital_name = name + " Offre en ligne"
    venues_by_name['THEATRE DU SOLEIL (ON)'] = create_venue(
        offerer,
        is_virtual=True,
        name=digital_name,
        siret=None
    )

    PcObject.check_and_save(*venues_by_name.values())

    return venues_by_name
