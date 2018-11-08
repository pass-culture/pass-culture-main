from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing_offer

def create_scratch_thing_offers(things_by_name, venues_by_name):

    thing_offers_by_name = {}

    thing_offers_by_name['Ravage / THEATRE DE L ODEON'] = create_thing_offer(
        venues_by_name['THEATRE DE L ODEON'],
        is_active=True,
        thing=things_by_name['Ravage']
    )

    thing_offers_by_name['Le Monde Diplomatique / THEATRE DE L ODEON (OL)'] = create_thing_offer(
        venues_by_name['THEATRE DE L ODEON (OL)'],
        is_active=True,
        thing=things_by_name['Le Monde Diplomatique']
    )

    return thing_offers_by_name
