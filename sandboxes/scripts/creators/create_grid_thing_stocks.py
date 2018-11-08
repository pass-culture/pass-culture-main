from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_stock_from_offer

def create_grid_thing_stocks(thing_offers_by_name):
    logger.info('create_grid_thing_stocks')

    thing_stocks_by_name = {}

    for thing_offer in thing_offers_by_name.values():
        thing_offer = create_stock_from_offer(thing_offer,
            available=10,
            price=10
        )
    
    PcObject.check_and_save(*thing_stocks_by_name.values())

    return thing_stocks_by_name
