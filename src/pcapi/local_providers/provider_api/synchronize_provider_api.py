from datetime import datetime
import logging
import time
from typing import Dict
from typing import Generator
from typing import List
from typing import Set
from typing import Tuple
from typing import Union

from flask import current_app as app
from sqlalchemy.sql.sqltypes import DateTime

from pcapi.connectors import redis
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.repository import get_offers_map_by_id_at_providers
from pcapi.core.offers.repository import get_products_map_by_id_at_providers
from pcapi.core.offers.repository import get_stocks_by_id_at_providers
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.models import Product
from pcapi.models import Venue
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.models.provider import Provider
from pcapi.models.venue_provider import VenueProvider
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.validation.models.entity_validator import validate


logger = logging.getLogger(__name__)


def check_siret_can_be_synchronized(siret: str, provider: Provider) -> bool:
    provider_api = provider.getProviderAPI()
    return provider_api.is_siret_registered(siret)


def synchronize_venue_provider(venue_provider: VenueProvider) -> None:
    venue = venue_provider.venue
    provider = venue_provider.provider
    start_sync_date = datetime.utcnow()

    start = time.perf_counter()
    logger.info("Starting synchronization of venue=%s provider=%s", venue.id, provider.name)
    provider_api = provider.getProviderAPI()

    stats = {"new_offers": 0, "new_stocks": 0, "updated_stocks": 0}
    for raw_stocks in _get_stocks_by_batch(venue.siret, provider_api, venue_provider.lastSyncDate):
        stock_details = _build_stock_details_from_raw_stocks(raw_stocks, venue.siret)

        products_provider_references = [stock_detail["products_provider_reference"] for stock_detail in stock_details]
        products_by_provider_reference = get_products_map_by_id_at_providers(products_provider_references)

        stock_details = [
            stock for stock in stock_details if stock["products_provider_reference"] in products_by_provider_reference
        ]

        offers_provider_references = [stock_detail["offers_provider_reference"] for stock_detail in stock_details]
        offers_by_provider_reference = get_offers_map_by_id_at_providers(offers_provider_references)

        new_offers = _build_new_offers_from_stock_details(
            stock_details, offers_by_provider_reference, products_by_provider_reference, venue_provider
        )
        new_offers_references = [new_offer.idAtProviders for new_offer in new_offers]

        db.session.bulk_save_objects(new_offers)
        stats["new_offers"] += len(new_offers)

        new_offers_by_provider_reference = get_offers_map_by_id_at_providers(new_offers_references)
        offers_by_provider_reference = {**offers_by_provider_reference, **new_offers_by_provider_reference}

        stocks_provider_references = [stock["stocks_provider_reference"] for stock in stock_details]
        stocks_by_provider_reference = get_stocks_by_id_at_providers(stocks_provider_references)
        update_stock_mapping, new_stocks, offer_ids = _get_stocks_to_upsert(
            stock_details,
            stocks_by_provider_reference,
            offers_by_provider_reference,
            products_by_provider_reference,
        )

        db.session.bulk_save_objects(new_stocks)
        db.session.bulk_update_mappings(Stock, update_stock_mapping)
        stats["new_stocks"] += len(new_stocks)
        stats["updated_stocks"] += len(update_stock_mapping)

        db.session.commit()

        _reindex_offers(offer_ids)

    venue_provider.lastSyncDate = start_sync_date
    repository.save(venue_provider)
    logger.info(
        "Ended synchronization of venue=%s provider=%s",
        venue.id,
        provider.name,
        extra={
            "venue": venue.id,
            "provider": provider.name,
            "duration": time.perf_counter() - start,
            **stats,
        },
    )


def _get_stocks_by_batch(siret: str, provider_api: ProviderAPI, modified_since: DateTime) -> Generator:
    last_processed_provider_reference = ""

    while True:
        response = provider_api.validated_stocks(
            siret=siret,
            last_processed_reference=last_processed_provider_reference,
            modified_since=modified_since.strftime("%Y-%m-%dT%H:%M:%SZ") if modified_since else "",
        )
        raw_stocks = response.get("stocks", [])

        if not raw_stocks:
            break

        yield raw_stocks

        last_processed_provider_reference = raw_stocks[-1]["ref"]


def _build_stock_details_from_raw_stocks(raw_stocks: List[Dict], venue_siret: str) -> List[Dict]:
    stock_details = []
    for stock in raw_stocks:
        stock_details.append(
            {
                "products_provider_reference": stock["ref"],
                "offers_provider_reference": stock["ref"] + "@" + venue_siret,
                "stocks_provider_reference": stock["ref"] + "@" + venue_siret,
                "available_quantity": stock["available"],
            }
        )

    return stock_details


def _build_new_offers_from_stock_details(
    stock_details: List,
    existing_offers_by_provider_reference: Dict[str, int],
    products_by_provider_reference: Dict[str, Product],
    venue_provider: VenueProvider,
) -> List[Offer]:
    new_offers = []
    for stock_detail in stock_details:
        if stock_detail["offers_provider_reference"] in existing_offers_by_provider_reference:
            continue

        product = products_by_provider_reference[stock_detail["products_provider_reference"]]
        offer = _build_new_offer(
            venue_provider.venue,
            product,
            id_at_providers=stock_detail["offers_provider_reference"],
            provider_id=venue_provider.providerId,
        )

        if not _validate_stock_or_offer(offer):
            continue

        new_offers.append(offer)

    return new_offers


def _get_stocks_to_upsert(
    stock_details: List[Dict],
    stocks_by_provider_reference: Dict[str, Dict],
    offers_by_provider_reference: Dict[str, int],
    products_by_provider_reference: Dict[str, Product],
) -> Tuple[List[Dict], List[Stock], Set[int]]:
    update_stock_mapping = []
    new_stocks = []
    offer_ids = set()

    for stock_detail in stock_details:
        stock_provider_reference = stock_detail["stocks_provider_reference"]
        product = products_by_provider_reference[stock_detail["products_provider_reference"]]
        book_price = product.extraData["prix_livre"]
        if stock_provider_reference in stocks_by_provider_reference:
            stock = stocks_by_provider_reference[stock_provider_reference]

            update_stock_mapping.append(
                {
                    "id": stock["id"],
                    "quantity": stock_detail["available_quantity"] + stock["booking_quantity"],
                    "rawProviderQuantity": stock_detail["available_quantity"],
                    "price": book_price,
                }
            )
            offer_ids.add(offers_by_provider_reference[stock_detail["offers_provider_reference"]])

        else:
            stock = _build_stock_from_stock_detail(
                stock_detail,
                offers_by_provider_reference[stock_detail["offers_provider_reference"]],
                book_price,
            )
            if not _validate_stock_or_offer(stock):
                continue

            new_stocks.append(stock)
            offer_ids.add(stock.offerId)

    return update_stock_mapping, new_stocks, offer_ids


def _build_stock_from_stock_detail(stock_detail: Dict, offers_id: int, price: float) -> Stock:
    return Stock(
        quantity=stock_detail["available_quantity"],
        rawProviderQuantity=stock_detail["available_quantity"],
        bookingLimitDatetime=None,
        offerId=offers_id,
        price=price,
        dateModified=datetime.now(),
        idAtProviders=stock_detail["stocks_provider_reference"],
    )


def _validate_stock_or_offer(model: Union[Offer, Stock]) -> bool:
    model_api_errors = validate(model)
    if model_api_errors.errors.keys():
        logger.exception(
            "[SYNC] errors while trying to add stock or offer with ref %s: %s",
            model.idAtProviders,
            model_api_errors.errors,
        )
        return False

    return True


def _build_new_offer(venue: Venue, product: Product, id_at_providers: str, provider_id: str) -> Offer:
    return Offer(
        bookingEmail=venue.bookingEmail,
        description=product.description,
        extraData=product.extraData,
        idAtProviders=id_at_providers,
        lastProviderId=provider_id,
        name=product.name,
        productId=product.id,
        venueId=venue.id,
        type=product.type,
    )


def _reindex_offers(offer_ids: Set[int]) -> None:
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        for offer_id in offer_ids:
            redis.add_offer_id(client=app.redis_client, offer_id=offer_id)
