from decimal import Decimal
from typing import Callable, Dict, Optional

from domain.price_rule import PriceRule
from domain.stock_provider.stock_provider_repository import StockProviderRepository
from local_providers import AllocineStocks, FnacStocks, LibrairesStocks, PraxielStocks, TiteLiveStocks
from models import AllocineVenueProvider, AllocineVenueProviderPriceRule, ApiErrors, VenueProvider, VenueSQLEntity
from repository import repository
from repository.allocine_pivot_queries import get_allocine_theaterId_for_venue
from utils.human_ids import dehumanize
from validation.routes.venues import check_existing_venue

STANDARD_STOCK_PROVIDERS = {
    FnacStocks: 'FNAC',
    LibrairesStocks: 'LesLibraires',
    PraxielStocks: 'Praxiel/Inférence',
    TiteLiveStocks: 'TiteLive',
}
ERROR_CODE_PROVIDER_NOT_SUPPORTED = 400
ERROR_CODE_SIRET_NOT_SUPPORTED = 422


def connect_provider_to_venue(provider_class: object,
                              stock_provider_repository: StockProviderRepository,
                              venue_provider_payload: Dict,
                              find_by_id: Callable) -> VenueProvider:
    venue_id = dehumanize(venue_provider_payload['venueId'])
    venue = find_by_id(venue_id)
    check_existing_venue(venue)
    if provider_class == AllocineStocks:
        new_venue_provider = _connect_allocine_to_venue(venue, venue_provider_payload)
    elif provider_class in STANDARD_STOCK_PROVIDERS:
        _check_venue_can_be_synchronized_with_provider(venue.siret,
                                                       stock_provider_repository.can_be_synchronized,
                                                       STANDARD_STOCK_PROVIDERS[provider_class])
        new_venue_provider = _connect_stock_providers_to_venue(venue, venue_provider_payload)
    else:
        api_errors = ApiErrors()
        api_errors.status_code = ERROR_CODE_PROVIDER_NOT_SUPPORTED
        api_errors.add_error('provider', 'Provider non pris en charge')
        raise api_errors

    return new_venue_provider


def _connect_allocine_to_venue(venue: VenueSQLEntity, venue_provider_payload: Dict) -> AllocineVenueProvider:
    allocine_theater_id = get_allocine_theaterId_for_venue(venue)
    allocine_venue_provider = _create_allocine_venue_provider(allocine_theater_id, venue_provider_payload, venue)
    allocine_venue_provider_price_rule = _create_allocine_venue_provider_price_rule(allocine_venue_provider,
                                                                                    venue_provider_payload.get('price'))

    repository.save(allocine_venue_provider_price_rule)

    return allocine_venue_provider


def _connect_stock_providers_to_venue(venue: VenueSQLEntity, venue_provider_payload: Dict) -> VenueProvider:
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.providerId = dehumanize(venue_provider_payload['providerId'])
    venue_provider.venueIdAtOfferProvider = venue.siret

    repository.save(venue_provider)
    return venue_provider


def _create_allocine_venue_provider_price_rule(allocine_venue_provider: VenueProvider,
                                               price: Decimal) -> AllocineVenueProviderPriceRule:
    venue_provider_price_rule = AllocineVenueProviderPriceRule()
    venue_provider_price_rule.allocineVenueProvider = allocine_venue_provider
    venue_provider_price_rule.priceRule = PriceRule.default
    venue_provider_price_rule.price = price

    return venue_provider_price_rule


def _create_allocine_venue_provider(allocine_theater_id: str, venue_provider_payload: Dict,
                                    venue: VenueSQLEntity) -> AllocineVenueProvider:
    allocine_venue_provider = AllocineVenueProvider()
    allocine_venue_provider.venue = venue
    allocine_venue_provider.providerId = dehumanize(venue_provider_payload['providerId'])
    allocine_venue_provider.venueIdAtOfferProvider = allocine_theater_id
    allocine_venue_provider.isDuo = venue_provider_payload.get('isDuo')
    allocine_venue_provider.quantity = venue_provider_payload.get('quantity')

    return allocine_venue_provider


def _check_venue_can_be_synchronized_with_provider(siret: str,
                                                   can_be_synchronized: Callable,
                                                   provider_name: str) -> None:
    if not siret or not can_be_synchronized(siret):
        api_errors = ApiErrors()
        api_errors.status_code = ERROR_CODE_SIRET_NOT_SUPPORTED
        api_errors.add_error('provider', _get_synchronization_error_message(provider_name, siret))
        raise api_errors


def _get_synchronization_error_message(provider_name: str, siret: Optional[str]) -> str:
    if siret:
        return f'L’importation d’offres avec {provider_name} n’est pas disponible pour le SIRET {siret}'
    else:
        return f'L’importation d’offres avec {provider_name} n’est pas disponible sans SIRET associé au lieu. Ajoutez un SIRET pour pouvoir importer les offres.'
