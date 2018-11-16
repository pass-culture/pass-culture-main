from models.offer_type import ThingType
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing

def create_handmade_things():
    logger.info('create_handmade_things')

    things_by_name = {}

    things_by_name['Ravage'] = create_thing(thing_name="Ravage", thing_type=str(ThingType.LIVRE_EDITION),
                                            author_name="Barjavel")

    things_by_name['Le Monde Diplomatique'] = create_thing(thing_name="Le Monde Diplomatique",
                                                           thing_type=str(ThingType.PRESSE_ABO),
                                                           media_urls=['https://www.monde-diplomatique.fr/'],
                                                           author_name="Le Monde", is_national=True)

    PcObject.check_and_save(*things_by_name.values())

    return things_by_name
