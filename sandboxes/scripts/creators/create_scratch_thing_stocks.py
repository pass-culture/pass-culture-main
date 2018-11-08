from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing_stock

def create_scratch_thing_stocks(offers_by_name):

    thing_stocks_by_name = {}

    thing_stocks_by_name['Ravage / THEATRE DE L ODEON / 50 / 50'] = create_thing_stock(
        available=50,
        offer=offers_by_name['Ravage / THEATRE DE L ODEON'],
        price=50
    )

    return thing_stocks_by_name
