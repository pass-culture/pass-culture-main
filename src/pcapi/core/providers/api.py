from datetime import datetime
import logging
import subprocess
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

from flask import current_app as app

from pcapi.connectors import redis
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.validation import check_existing_venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.offers.repository import get_offers_map_by_id_at_providers
from pcapi.core.offers.repository import get_products_map_by_id_at_providers
from pcapi.core.offers.repository import get_stocks_by_id_at_providers
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_provider_enabled_for_pro_by_id
from pcapi.infrastructure.container import api_fnac_stocks
from pcapi.infrastructure.container import api_libraires_stocks
from pcapi.infrastructure.container import api_praxiel_stocks
from pcapi.infrastructure.container import api_titelive_stocks
from pcapi.models import ApiErrors
from pcapi.models import Product
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository.venue_queries import find_by_id
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.use_cases.connect_venue_to_allocine import connect_venue_to_allocine
from pcapi.utils.human_ids import dehumanize
from pcapi.validation.models.entity_validator import validate
from pcapi.validation.routes.venue_providers import check_existing_provider


logger = logging.getLogger(__name__)


def create_venue_provider(venue_provider: PostVenueProviderBody) -> VenueProvider:
    provider_id = dehumanize(venue_provider.providerId)
    provider = get_provider_enabled_for_pro_by_id(provider_id)
    check_existing_provider(provider)

    venue_id = dehumanize(venue_provider.venueId)
    venue = find_by_id(venue_id)
    check_existing_venue(venue)

    if provider.localClass == "AllocineStocks":
        new_venue_provider = connect_venue_to_allocine(venue, venue_provider)
    else:
        new_venue_provider = connect_venue_to_provider(venue, provider, venue_provider.venueIdAtOfferProvider)

    _run_first_synchronization(new_venue_provider)

    return new_venue_provider


def _run_first_synchronization(new_venue_provider: VenueProvider) -> None:
    if not feature_queries.is_active(FeatureToggle.SYNCHRONIZE_VENUE_PROVIDER_IN_WORKER):
        subprocess.Popen(
            [
                "python",
                "src/pcapi/scripts/pc.py",
                "update_providables",
                "--venue-provider-id",
                str(new_venue_provider.id),
            ]
        )
        return

    # FIXME (apibrac, 2021-04-19): we shouldn't import infra function from core
    from pcapi.workers.venue_provider_job import venue_provider_job

    venue_provider_job.delay(new_venue_provider.id)


SPECIFIC_STOCK_PROVIDER = {
    "LibrairesStocks": api_libraires_stocks,
    "FnacStocks": api_fnac_stocks,
    "TiteLiveStocks": api_titelive_stocks,
    "PraxielStocks": api_praxiel_stocks,
}
ERROR_CODE_PROVIDER_NOT_SUPPORTED = 400
ERROR_CODE_SIRET_NOT_SUPPORTED = 422


def connect_venue_to_provider(venue: Venue, provider: Provider, venueIdAtOfferProvider: str = None) -> VenueProvider:
    id_at_provider = venueIdAtOfferProvider or venue.siret
    _check_provider_can_be_used(provider)
    _check_venue_can_be_synchronized_with_provider(id_at_provider, provider)

    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = provider
    venue_provider.venueIdAtOfferProvider = id_at_provider

    repository.save(venue_provider)
    return venue_provider


def _check_provider_can_be_used(
    provider: Provider,
) -> None:
    if not provider.implements_provider_api and provider.localClass not in SPECIFIC_STOCK_PROVIDER:
        api_errors = ApiErrors()
        api_errors.status_code = ERROR_CODE_PROVIDER_NOT_SUPPORTED
        api_errors.add_error("provider", "Provider non pris en charge")
        raise api_errors


def _check_venue_can_be_synchronized_with_provider(
    id_at_provider: str,
    provider: Provider,
) -> None:
    if not _siret_can_be_synchronized(id_at_provider, provider):
        api_errors = ApiErrors()
        api_errors.status_code = ERROR_CODE_SIRET_NOT_SUPPORTED
        api_errors.add_error("provider", _get_synchronization_error_message(provider.name, id_at_provider))
        raise api_errors


def _siret_can_be_synchronized(
    siret: str,
    provider: Provider,
) -> bool:
    if not siret:
        return False

    if provider.implements_provider_api:
        provider_api = provider.getProviderAPI()
        return provider_api.is_siret_registered(siret)

    return SPECIFIC_STOCK_PROVIDER[provider.localClass].can_be_synchronized(siret)


def _get_synchronization_error_message(provider_name: str, siret: Optional[str]) -> str:
    if siret:
        return f"L’importation d’offres avec {provider_name} n’est pas disponible pour le SIRET {siret}"
    return f"L’importation d’offres avec {provider_name} n’est pas disponible sans SIRET associé au lieu. Ajoutez un SIRET pour pouvoir importer les offres."


def synchronize_stocks(stock_details, venue: Venue, provider_id: Optional[int] = None):
    products_provider_references = [stock_detail["products_provider_reference"] for stock_detail in stock_details]
    products_by_provider_reference = get_products_map_by_id_at_providers(products_provider_references)

    stock_details = [
        stock for stock in stock_details if stock["products_provider_reference"] in products_by_provider_reference
    ]

    offers_provider_references = [stock_detail["offers_provider_reference"] for stock_detail in stock_details]
    offers_by_provider_reference = get_offers_map_by_id_at_providers(offers_provider_references)

    new_offers = _build_new_offers_from_stock_details(
        stock_details, offers_by_provider_reference, products_by_provider_reference, venue, provider_id
    )
    new_offers_references = [new_offer.idAtProviders for new_offer in new_offers]

    db.session.bulk_save_objects(new_offers)

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

    db.session.commit()

    _reindex_offers(offer_ids)

    return {"new_offers": len(new_offers), "new_stocks": len(new_stocks), "updated_stocks": len(update_stock_mapping)}


def _build_new_offers_from_stock_details(
    stock_details: List,
    existing_offers_by_provider_reference: Dict[str, int],
    products_by_provider_reference: Dict[str, Product],
    venue: Venue,
    provider_id: Optional[int],
) -> List[Offer]:
    new_offers = []
    for stock_detail in stock_details:
        if stock_detail["offers_provider_reference"] in existing_offers_by_provider_reference:
            continue
        if not stock_detail["available_quantity"]:
            continue

        product = products_by_provider_reference[stock_detail["products_provider_reference"]]
        offer = _build_new_offer(
            venue,
            product,
            id_at_providers=stock_detail["offers_provider_reference"],
            provider_id=provider_id,
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
        book_price = stock_detail.get("price") or float(product.extraData["prix_livre"])
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
            if not stock_detail["available_quantity"]:
                continue
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
