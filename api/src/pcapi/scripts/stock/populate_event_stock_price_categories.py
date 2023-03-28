# This script can be deleted with FF WIP_ENABLE_MULTI_PRICE_STOCKS
import datetime
import decimal
from itertools import groupby
import logging
import math
import typing

import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
from pcapi.models import db


CHUNK_SIZE = 500

logger = logging.getLogger(__name__)


def get_event_offers(creation_date: datetime.datetime | None) -> typing.Generator[offers_models.Offer, None, None]:
    query = offers_models.Offer.query.filter(offers_models.Offer.isEvent == True).order_by(
        offers_models.Offer.dateCreated
    )
    if creation_date:
        query = query.filter(offers_models.Offer.dateCreated >= creation_date)
    event_count = query.count()
    max_chunk = math.ceil(event_count / CHUNK_SIZE)
    logger.info("Event Count : %s", event_count)
    logger.info("Chunks Count : %s", max_chunk)
    for chunk in range(max_chunk):
        logger.info("Chunk %s/max_chunk", (chunk + 1) / max_chunk)
        for offer in query.offset(chunk * CHUNK_SIZE).limit(CHUNK_SIZE):
            yield offer
        db.session.commit()


def _get_or_create_price_category(
    price_category_label: offers_models.PriceCategoryLabel, price: decimal.Decimal, offer: offers_models.Offer
) -> offers_models.PriceCategory:
    price_categories = (
        offers_models.PriceCategory.query.filter_by(price=price, offer=offer)
        .order_by(offers_models.PriceCategory.id)
        .all()
    )
    if not price_categories:
        return offers_models.PriceCategory(price=price, offer=offer, priceCategoryLabel=price_category_label)

    price_category = price_categories[0]
    if price_category.label != price_category_label.label:
        price_category.priceCategoryLabel = price_category_label

    return price_category


def populate_event_stock_price_categories(creation_date: datetime.datetime | None) -> None:
    event_offers_query = get_event_offers(creation_date)

    for offer in event_offers_query:
        stock_prices = {stock.price for stock in offer.activeStocks}
        if len(stock_prices) == 1:
            price_category_label = offers_api.get_or_create_label("Tarif unique", offer.venue)
            price_category = _get_or_create_price_category(price_category_label, stock_prices.pop(), offer)
            for stock in offer.activeStocks:
                stock.priceCategory = price_category

        else:
            sorted_stocks = sorted(offer.activeStocks, key=lambda d: d.price)
            for index, (price, stocks) in enumerate(groupby(sorted_stocks, key=lambda d: d.price), start=1):
                price_category_label = offers_api.get_or_create_label(f"Tarif {index}", offer.venue)
                price_category = _get_or_create_price_category(price_category_label, price, offer)
                for stock in stocks:
                    stock.priceCategory = price_category
        db.session.add(offer)
