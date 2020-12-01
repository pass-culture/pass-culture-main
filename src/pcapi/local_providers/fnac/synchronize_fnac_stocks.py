from datetime import datetime
from typing import Dict
from typing import Generator
from typing import List
from typing import Tuple
from typing import Union

from pcapi import settings
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.repository import get_offers_map_by_id_at_providers
from pcapi.core.offers.repository import get_products_map_by_id_at_providers
from pcapi.core.offers.repository import get_stocks_by_id_at_providers
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.models import Product
from pcapi.models import VenueSQLEntity
from pcapi.models.db import db
from pcapi.utils.logger import logger
from pcapi.validation.models.entity_validator import validate


def synchronize_venue_stocks_from_fnac(venue: VenueSQLEntity) -> None:
    logger.info("Starting synchronization of venue=%s provider=fnac", venue.id)
    fnac_api = ProviderAPI(
        api_url=settings.FNAC_API_URL,
        name="Fnac",
        authentication_token=settings.FNAC_API_TOKEN,
    )

    for raw_stocks in _get_stocks_by_batch(venue.siret, fnac_api):
        stock_details = _build_stock_details_from_raw_stocks(raw_stocks, venue.siret)

        products_fnac_references = [stock_detail["products_fnac_reference"] for stock_detail in stock_details]
        products_by_fnac_reference = get_products_map_by_id_at_providers(products_fnac_references)

        stock_details = [
            stock for stock in stock_details if stock["products_fnac_reference"] in products_by_fnac_reference
        ]

        offers_fnac_references = [stock_detail["offers_fnac_reference"] for stock_detail in stock_details]
        offers_by_fnac_reference = get_offers_map_by_id_at_providers(offers_fnac_references)

        new_offers = _build_new_offers_from_stock_details(
            stock_details, offers_by_fnac_reference, products_by_fnac_reference, venue
        )
        new_offers_references = [new_offer.idAtProviders for new_offer in new_offers]

        db.session.bulk_save_objects(new_offers)

        new_offers_by_fnac_reference = get_offers_map_by_id_at_providers(new_offers_references)
        offers_by_fnac_reference = {**offers_by_fnac_reference, **new_offers_by_fnac_reference}

        stocks_fnac_references = [stock["stocks_fnac_reference"] for stock in stock_details]
        stocks_by_fnac_reference = get_stocks_by_id_at_providers(stocks_fnac_references)

        update_stock_mapping, new_stocks = _get_stocks_to_upsert(
            stock_details, stocks_by_fnac_reference, offers_by_fnac_reference
        )

        db.session.bulk_save_objects(new_stocks)
        db.session.bulk_update_mappings(Stock, update_stock_mapping)

        db.session.commit()

    logger.info("Ending synchronization of venue=%s provider=fnac", venue.id)


def _get_stocks_by_batch(siret: str, fnac_api: ProviderAPI) -> Generator:
    last_processed_fnac_reference = ""

    while True:
        fnac_responses = fnac_api.validated_stocks(
            siret=siret,
            last_processed_reference=last_processed_fnac_reference,
            modified_since="",  # Fnac API does not handle this parameter
        )
        raw_stocks = fnac_responses.get("stocks", [])

        if not raw_stocks:
            break

        yield raw_stocks

        last_processed_fnac_reference = raw_stocks[-1]["ref"]


def _build_stock_details_from_raw_stocks(raw_stocks: List[Dict], venue_siret: str) -> List[Dict]:
    stock_details = []
    for stock in raw_stocks:
        stock_details.append(
            {
                "products_fnac_reference": stock["ref"],
                "offers_fnac_reference": stock["ref"] + "@" + venue_siret,
                "stocks_fnac_reference": stock["ref"] + "@" + venue_siret,
                "available_quantity": stock["available"],
                "price": stock["price"],
            }
        )

    return stock_details


def _build_new_offers_from_stock_details(
    stock_details: List,
    existing_offers_by_fnac_reference: Dict[str, int],
    products_by_fnac_reference: Dict[str, Product],
    venue: VenueSQLEntity,
) -> List[Offer]:
    new_offers = []
    for stock_detail in stock_details:
        if stock_detail["offers_fnac_reference"] in existing_offers_by_fnac_reference:
            continue

        product = products_by_fnac_reference[stock_detail["products_fnac_reference"]]
        offer = _build_new_offer(venue, product, id_at_providers=stock_detail["offers_fnac_reference"])

        if not _validate_stock_or_offer(offer):
            continue

        new_offers.append(offer)

    return new_offers


def _get_stocks_to_upsert(
    stock_details: List[Dict], stocks_by_fnac_reference: Dict[str, Dict], offers_by_fnac_reference: Dict[str, int]
) -> Tuple[List, List[Stock]]:
    update_stock_mapping = []
    new_stocks = []

    for stock_detail in stock_details:
        if stock_detail["stocks_fnac_reference"] in stocks_by_fnac_reference:
            stock = stocks_by_fnac_reference[stock_detail["stocks_fnac_reference"]]
            update_stock_mapping.append(
                {
                    "id": stock["id"],
                    "quantity": stock_detail["available_quantity"] + stock["booking_quantity"],
                    "price": stock_detail["price"],
                }
            )

        else:
            stock = _build_stock_from_stock_detail(
                stock_detail, offers_by_fnac_reference[stock_detail["offers_fnac_reference"]]
            )
            if not _validate_stock_or_offer(stock):
                continue

            new_stocks.append(stock)

    return update_stock_mapping, new_stocks


def _build_stock_from_stock_detail(stock_detail: Dict, offers_id: int) -> Stock:
    return Stock(
        quantity=stock_detail["available_quantity"],
        bookingLimitDatetime=None,
        offerId=offers_id,
        price=stock_detail["price"],
        dateModified=datetime.now(),
        idAtProviders=stock_detail["stocks_fnac_reference"],
    )


def _validate_stock_or_offer(model: Union[Offer, Stock]) -> bool:
    model_api_errors = validate(model)
    if model_api_errors.errors.keys():
        logger.exception(
            "[FNAC SYNC] errors while trying to add stock or offer with ref %s: %s",
            model.idAtProviders,
            model_api_errors.errors,
        )
        return False

    return True


def _build_new_offer(venue: VenueSQLEntity, product: Product, id_at_providers: str) -> Offer:
    return Offer(
        bookingEmail=venue.bookingEmail,
        description=product.description,
        extraData=product.extraData,
        idAtProviders=id_at_providers,
        name=product.name,
        productId=product.id,
        venueId=venue.id,
        type=product.type,
    )
