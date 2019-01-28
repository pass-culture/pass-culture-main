from models.offer_type import ThingType
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing

def create_handmade_things():
    logger.info('create_handmade_things')

    things_by_name = {}

    things_by_name['Ravage'] = create_thing(thing_name="Ravage", thing_type=ThingType.LIVRE_EDITION,
                                            author_name="Barjavel")

    things_by_name['Le Monde Diplomatique'] = create_thing(thing_name="Le Monde Diplomatique",
                                                           thing_type=ThingType.PRESSE_ABO,
                                                           media_urls=['https://www.monde-diplomatique.fr/'],
                                                           author_name="Le Monde", is_national=True)

    things_by_name['pass Culture Activation'] = create_thing(thing_name="Activation en ligne",
                                                           thing_type=ThingType.ACTIVATION,
                                                           media_urls=['http://app.passculture.beta.gouv.fr/'],
                                                           author_name="pass Culture", is_national=True)

    PcObject.check_and_save(*things_by_name.values())

    logger.info('created {} things'.format(len(things_by_name)))

    return things_by_name
