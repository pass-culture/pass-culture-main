from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_venue

def create_handmade_venues(offerers_by_name):
    logger.info('create_handmade_venues')

    venues_by_name = {}

    offerer = offerers_by_name['LE GRAND REX PARIS']
    name = offerer.name
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

    offerer = offerers_by_name['LE GRAND REX PARIS']
    name = offerer.name + " (Offre en ligne)"
    venues_by_name[name] = create_venue(
        offerer,
        is_virtual=True,
        name=name,
        siret=None
    )

    offerer = offerers_by_name["THEATRE DE L ODEON"]
    name = offerer.name
    venues_by_name[name] = create_venue(
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

    offerer = offerers_by_name["THEATRE DE L ODEON"]
    name = offerer.name + " (Offre en ligne)"
    venues_by_name[name] = create_venue(
        offerer,
        is_virtual=True,
        name=name,
        siret=None
    )

    offerer = offerers_by_name["THEATRE DU SOLEIL"]
    name = offerer.name + " (Offre en ligne)"
    venues_by_name[name] = create_venue(
        offerer,
        is_virtual=True,
        name=name,
        siret=None
    )

    offerer = offerers_by_name["KWATA"]
    name = offerer.name
    venues_by_name[name] = create_venue(
        offerer,
        address=offerer.address,
        booking_email="fake3@email.com",
        city=offerer.city,
        latitude=4.836694,
        longitude=-52.3279538,
        name=name,
        postal_code=offerer.postalCode,
        siret=offerer.siren + "00033"
    )

    offerer = offerers_by_name["KWATA"]
    name = offerer.name + " (Offre en ligne)"
    venues_by_name[name] = create_venue(
        offerer,
        is_virtual=True,
        name=name,
        siret=None
    )

    PcObject.check_and_save(*venues_by_name.values())

    return venues_by_name
