from repository import repository
from sandboxes.scripts.utils.select import remove_every
from tests.model_creators.specific_creators import create_stock_from_offer
from tests.test_utils import get_price_by_short_name, get_occurrence_short_name
from utils.logger import logger

THING_OFFERS_WITH_STOCK_REMOVE_MODULO = 3


def create_industrial_thing_stocks(thing_offers_by_name):
    logger.info('create_industrial_thing_stocks')

    thing_stocks_by_name = {}
    short_names_to_increase_price = []

    thing_offer_items = list(thing_offers_by_name.items())

    thing_offer_items_with_stocks = remove_every(
        thing_offer_items,
        THING_OFFERS_WITH_STOCK_REMOVE_MODULO
    )

    for thing_offer_item_with_stocks in thing_offer_items_with_stocks:
        (thing_offer_with_stocks_name, thing_offer_with_stocks) = thing_offer_item_with_stocks
        quantity = 10

        short_name = get_occurrence_short_name(thing_offer_with_stocks_name)
        price = get_price_by_short_name(short_name)
        price_counter = short_names_to_increase_price.count(short_name)
        if price_counter > 2:
            price = price + price_counter
        short_names_to_increase_price.append(short_name)

        name = thing_offer_with_stocks_name + " / " + str(quantity) + " / " + str(price)
        thing_stocks_by_name[name] = create_stock_from_offer(thing_offer_with_stocks, price=price)

    repository.save(*thing_stocks_by_name.values())

    logger.info('created {} thing_stocks'.format(len(thing_stocks_by_name)))
