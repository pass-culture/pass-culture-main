from datetime import datetime
from datetime import time
from datetime import timedelta
import decimal
import logging

from pcapi.core.categories import subcategories
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models.event_occurence import EventOccurrence
from pcapi.sandboxes.scripts.utils.select import remove_every
import pcapi.utils.date as date_utils

from . import utils


logger = logging.getLogger(__name__)


TODAY = datetime.combine(datetime.utcnow(), time(hour=20))
EVENT_OCCURRENCE_BEGINNING_DATETIMES = [
    TODAY,
    TODAY + timedelta(days=2),
    TODAY + timedelta(days=15),
]

EVENT_OFFERS_WITH_OCCURRENCES_REMOVE_MODULO = 3


def create_industrial_event_occurrences(
    event_offers_by_name: dict[str, offers_models.Offer],
) -> dict[str, EventOccurrence]:
    logger.info("create_industrial_event_occurrences")

    event_occurrences_by_name = {}

    event_offers = list(event_offers_by_name.values())
    short_names_to_increase_price: list[str] = []

    event_offers_with_occurrences = remove_every(event_offers, EVENT_OFFERS_WITH_OCCURRENCES_REMOVE_MODULO)

    for event_offer_with_occurrences in event_offers_with_occurrences:
        price_categories: dict[decimal.Decimal, offers_models.PriceCategory] = {}
        for index, beginning_datetime in enumerate(EVENT_OCCURRENCE_BEGINNING_DATETIMES, start=1):
            name = "{} / {} / {} ".format(
                event_offer_with_occurrences.name,
                event_offer_with_occurrences.venue.name,
                beginning_datetime.strftime(date_utils.DATE_ISO_FORMAT),
            )

            short_name = utils.get_occurrence_short_name(name)
            price = utils.get_price_by_short_name(short_name)
            price_counter = short_names_to_increase_price.count(short_name)
            if price_counter > 2:
                price = price + price_counter

            if (
                event_offer_with_occurrences.product
                and event_offer_with_occurrences.product.subcategoryId in subcategories.ACTIVATION_SUBCATEGORIES
            ):
                price = decimal.Decimal(0)

            if price in price_categories:
                price_category = price_categories[price]
            else:
                price_category = offers_factories.PriceCategoryFactory.create(
                    offer=event_offer_with_occurrences,
                    price=price,
                    priceCategoryLabel=offers_api.get_or_create_label(
                        f"Tarif {index}", event_offer_with_occurrences.venue
                    ),
                )
                price_categories[price] = price_category

            short_names_to_increase_price.append(short_name)
            event_occurrences_by_name[name] = EventOccurrence(
                beginning_datetime=beginning_datetime,
                offer=event_offer_with_occurrences,
                price=price,
                price_category=price_category,
            )

    return event_occurrences_by_name
