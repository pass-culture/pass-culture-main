from decimal import Decimal
import logging

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.repository import repository
from pcapi.sandboxes.scripts.creators.data.create_data_event_occurrences import EventOccurrence

from .utils import get_occurrence_short_name
from .utils import get_price_by_short_name


logger = logging.getLogger(__name__)


def create_data_event_stocks(event_occurrences_by_name: dict[str, EventOccurrence]) -> None:
    logger.info("create_data_event_stocks_data")

    event_stocks_by_name = {}
    short_names_to_increase_price: list[str] = []

    event_occurrence_items = list(event_occurrences_by_name.items())

    event_occurrence_items_with_stocks = event_occurrence_items
    for event_occurrence_item_with_stocks in event_occurrence_items_with_stocks:
        (event_occurrence_with_stocks_name, event_occurrence_with_stocks) = event_occurrence_item_with_stocks
        available = 20

        short_name = get_occurrence_short_name(event_occurrence_with_stocks_name)
        price = get_price_by_short_name(short_name)
        price_counter = short_names_to_increase_price.count(short_name)
        if price_counter > 2:
            price = price + price_counter
        short_names_to_increase_price.append(short_name)

        if (
            event_occurrence_with_stocks.offer.product
            and event_occurrence_with_stocks.offer.product.subcategoryId in subcategories.ACTIVATION_SUBCATEGORIES
        ):
            price = Decimal(0)

        name = event_occurrence_with_stocks_name + " / " + str(available) + " / " + str(price) + " / " + "DATA"

        event_stocks_by_name[name] = offers_factories.EventStockFactory(
            offer=event_occurrence_with_stocks.offer,
            price=price,
            quantity=available,
            beginningDatetime=event_occurrence_with_stocks.beginningDatetime,
        )

    repository.save(*event_stocks_by_name.values())

    logger.info("created %d event_stocks", len(event_stocks_by_name))
