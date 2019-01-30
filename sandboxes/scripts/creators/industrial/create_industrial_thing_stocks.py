from models.pc_object import PcObject
from sandboxes.scripts.utils.select import remove_every
from utils.logger import logger
from utils.test_utils import create_stock_from_offer

THING_OFFERS_WITH_STOCK_REMOVE_MODULO = 3

def create_industrial_thing_stocks(thing_offers_by_name):
    logger.info('create_industrial_thing_stocks')

    thing_stocks_by_name = {}

    thing_offer_items = list(thing_offers_by_name.items())

    thing_offer_items_with_stocks = remove_every(
        thing_offer_items,
        THING_OFFERS_WITH_STOCK_REMOVE_MODULO
    )

    for thing_offer_item_with_stocks in thing_offer_items_with_stocks:
        (thing_offer_with_stocks_name, thing_offer_with_stocks) = thing_offer_item_with_stocks
        available = 10
        price = 10
        name = thing_offer_with_stocks_name + " / " + str(available) + " / " + str(price)
        thing_stocks_by_name[name] = create_stock_from_offer(
            thing_offer_with_stocks,
            available=available,
            price=price
        )

    PcObject.check_and_save(*thing_stocks_by_name.values())

    logger.info('created {} thing_stocks'.format(len(thing_stocks_by_name)))

    return thing_stocks_by_name
