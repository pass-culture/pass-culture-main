import logging

import pcapi.core.offers.factories as offers_factories
from pcapi.models import db
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_event_occurrences import EventOccurrence
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.sandboxes.scripts.utils.select import remove_every


logger = logging.getLogger(__name__)


EVENT_OCCURRENCES_WITH_STOCKS_REMOVE_MODULO = 4


@log_func_duration
def create_industrial_event_stocks(event_occurrences_by_name: dict[str, EventOccurrence]) -> None:
    logger.info("create_industrial_event_stocks")

    event_stocks_by_name = {}
    event_occurrence_items = list(event_occurrences_by_name.items())

    event_occurrence_items_with_stocks = remove_every(
        event_occurrence_items, EVENT_OCCURRENCES_WITH_STOCKS_REMOVE_MODULO
    )

    for event_occurrence_item_with_stocks in event_occurrence_items_with_stocks:
        (event_occurrence_with_stocks_name, event_occurrence_with_stocks) = event_occurrence_item_with_stocks
        available = 20
        name = (
            event_occurrence_with_stocks_name + " / " + str(available) + " / " + str(event_occurrence_with_stocks.price)
        )

        event_stocks_by_name[name] = offers_factories.EventStockFactory.create(
            offer=event_occurrence_with_stocks.offer,
            price=event_occurrence_with_stocks.price,
            quantity=available,
            beginningDatetime=event_occurrence_with_stocks.beginningDatetime,
            priceCategory=event_occurrence_with_stocks.price_category,
        )

    db.session.add_all(event_stocks_by_name.values())
    db.session.commit()

    logger.info("created %d event_stocks", len(event_stocks_by_name))
