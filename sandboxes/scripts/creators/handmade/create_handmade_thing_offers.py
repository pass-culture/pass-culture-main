from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing_offer

def create_handmade_thing_offers(things_by_name, venues_by_name):
    logger.info("create_handmade_thing_offers")

    thing_offers_by_name = {}

    thing_offers_by_name['Ravage / THEATRE DE L ODEON'] = create_thing_offer(
        venues_by_name['THEATRE DE L ODEON'],
        thing=things_by_name['Ravage']
    )

    thing_offers_by_name['Le Monde Diplomatique / THEATRE DE L ODEON (Offre en ligne)'] = create_thing_offer(
        venues_by_name['THEATRE DE L ODEON (Offre en ligne)'],
        thing=things_by_name['Le Monde Diplomatique']
    )

    thing_offers_by_name['pass Culture Activation / Activation (Offre en ligne)'] = create_thing_offer(
        venues_by_name['ACTIVATION (Offre en ligne)'],
        thing=things_by_name['pass Culture Activation']
    )

    PcObject.check_and_save(*thing_offers_by_name.values())

    logger.info('created {} thing_offers'.format(len(thing_offers_by_name)))

    return thing_offers_by_name
