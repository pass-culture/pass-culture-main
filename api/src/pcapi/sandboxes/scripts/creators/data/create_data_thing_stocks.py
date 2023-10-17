from decimal import Decimal
import logging

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.repository import repository


logger = logging.getLogger(__name__)
STOCK_QUANTITY_DATA = 100


def create_data_thing_stocks(thing_offers_by_name: dict[str, Offer]) -> None:
    logger.info("create_data_thing_stocks_data")

    thing_stocks_by_name = {}

    thing_offer_items = list(thing_offers_by_name.items())

    thing_offer_items_with_stocks = thing_offer_items
    for offer_name, offer in thing_offer_items_with_stocks:
        quantity = STOCK_QUANTITY_DATA
        price = Decimal(1)

        name = offer_name + " / " + str(quantity) + " / " + str(price)
        thing_stocks_by_name[name] = offers_factories.ThingStockFactory(
            offer=offer,
            quantity=quantity,
            price=price,
        )

    repository.save(*thing_stocks_by_name.values())

    logger.info("created %d thing_stocks", len(thing_stocks_by_name))
