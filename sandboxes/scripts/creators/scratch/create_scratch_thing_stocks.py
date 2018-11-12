from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_stock_from_offer

def create_scratch_thing_stocks(offers_by_name):
    logger.info("create_scratch_thing_stocks")

    thing_stocks_by_name = {}

    thing_stocks_by_name['Ravage / THEATRE DE L ODEON / 50 / 50'] = create_stock_from_offer(
        offers_by_name['Ravage / THEATRE DE L ODEON'],
        available=50,
        price=50
    )

    PcObject.check_and_save(*offers_by_name.values())

    return thing_stocks_by_name
