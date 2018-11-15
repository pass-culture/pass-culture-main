from models.pc_object import PcObject
from sandboxes.scripts.utils.ban import get_locations_from_postal_code
from utils.logger import logger
from utils.test_utils import create_offerer

def create_industrial_offerers(
    locations,
    starting_siren=222222222
):
    logger.info('create_industrial_offerers')

    incremented_siren = starting_siren

    offerers_by_name = {}

    for location in locations:

        name = 'STRUCTURE {} lat:{} lon:{}'.format(
            incremented_siren,
            location['latitude'],
            location['longitude']
        )

        offerers_by_name[name] = create_offerer(
            address=location['address'].upper(),
            city=location['city'],
            name=name,
            postal_code=location['postalCode'],
            siren=str(incremented_siren)
        )

        incremented_siren += 1

    PcObject.check_and_save(*offerers_by_name.values())

    return offerers_by_name
