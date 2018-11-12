from models.offer_types import ThingType
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing

def create_scratch_things():
    logger.info('create_scratch_things')

    things_by_name = {}

    things_by_name['Ravage'] = create_thing(
        thing_name="Ravage",
        thing_type=str(ThingType.LIVRE_EDITION)
    )

    things_by_name['Le Monde Diplomatique'] = create_thing(
        thing_name="Le Monde Diplomatique",
        thing_type=str(ThingType.PRESSE_ABO)
    )

    PcObject.check_and_save(*things_by_name.values())

    return things_by_name
