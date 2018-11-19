from models.pc_object import PcObject
from sandboxes.scripts.utils.ban import get_locations_from_postal_code
from utils.logger import logger
from utils.test_utils import create_offerer

MOCK_NAMES = [
    "Atelier Herbert Marcuse",
    "Club Dorothy",
    "Scope La Brique",
    "Les Perruches Swing",
    "Michel et son accordéon",
    "La librairie quantique",
    "Folie des anachorètes"
]

def create_industrial_offerers(
    locations,
    starting_siren=222222222
):
    logger.info('create_industrial_offerers')

    incremented_siren = starting_siren

    offerers_by_name = {}

    for (location_index, location) in enumerate(locations):

        mock_index = location_index % len(MOCK_NAMES)

        name = '{} lat:{} lon:{}'.format(
            incremented_siren,
            location['latitude'],
            location['longitude']
        )

        offerers_by_name[name] = create_offerer(
            address=location['address'].upper(),
            city=location['city'],
            name=MOCK_NAMES[mock_index],
            postal_code=location['postalCode'],
            siren=str(incremented_siren)
        )

        incremented_siren += 1

    PcObject.check_and_save(*offerers_by_name.values())

    logger.info('created {} offerers'.format(len(offerers_by_name)))

    return offerers_by_name
