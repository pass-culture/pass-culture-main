import logging

from pcapi.core.categories import subcategories
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence
from pcapi.repository import repository
from pcapi.sandboxes.scripts.utils.select import remove_every


logger = logging.getLogger(__name__)

from .utils import get_occurrence_short_name
from .utils import get_price_by_short_name


EVENT_OCCURRENCES_WITH_STOCKS_REMOVE_MODULO = 4


def create_industrial_event_stocks(event_occurrences_by_name):
    logger.info("create_industrial_event_stocks")

    event_stocks_by_name = {}
    short_names_to_increase_price = []

    event_occurrence_items = list(event_occurrences_by_name.items())

    event_occurrence_items_with_stocks = remove_every(
        event_occurrence_items, EVENT_OCCURRENCES_WITH_STOCKS_REMOVE_MODULO
    )

    for event_occurrence_item_with_stocks in event_occurrence_items_with_stocks:
        (event_occurrence_with_stocks_name, event_occurrence_with_stocks) = event_occurrence_item_with_stocks
        available = 20

        short_name = get_occurrence_short_name(event_occurrence_with_stocks_name)
        price = get_price_by_short_name(short_name)
        price_counter = short_names_to_increase_price.count(short_name)
        if price_counter > 2:
            price = price + price_counter
        short_names_to_increase_price.append(short_name)

        if event_occurrence_with_stocks["offer"].product.subcategoryId in subcategories.ACTIVATION_SUBCATEGORIES:
            price = 0

        name = event_occurrence_with_stocks_name + " / " + str(available) + " / " + str(price)

        event_stocks_by_name[name] = create_stock_from_event_occurrence(
            event_occurrence_with_stocks, price=price, quantity=available
        )

    repository.save(*event_stocks_by_name.values())

    logger.info("created %d event_stocks", len(event_stocks_by_name))
