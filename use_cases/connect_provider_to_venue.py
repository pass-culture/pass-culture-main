from decimal import Decimal
from typing import Dict

from domain.libraires import are_stocks_available_from_libraires_api
from local_providers import AllocineStocks, LibrairesStocks, TiteLiveStocks
from local_providers.local_provider import LocalProvider
from local_providers.price_rule import PriceRule
from models import AllocineVenueProvider, VenueSQLEntity, VenueProvider, AllocineVenueProviderPriceRule, ApiErrors
from repository import repository
from repository.allocine_pivot_queries import get_allocine_theaterId_for_venue
from repository.venue_queries import find_by_id
from utils.human_ids import dehumanize
from validation.routes.venues import check_existing_venue


def connect_provider_to_venue(provider_class: LocalProvider, venue_provider_payload: Dict) -> VenueProvider:
    venue_id = dehumanize(venue_provider_payload['venueId'])
    venue = find_by_id(venue_id)
    check_existing_venue(venue)
    if provider_class == AllocineStocks:
        new_venue_provider = _connect_allocine_to_venue(venue, venue_provider_payload)
    elif provider_class == LibrairesStocks:
        check_venue_can_be_synchronized_with_libraires(venue)
        new_venue_provider = _connect_titelive_or_libraires_to_venue(venue, venue_provider_payload)
    elif provider_class == TiteLiveStocks:
        new_venue_provider = _connect_titelive_or_libraires_to_venue(venue, venue_provider_payload)
    else:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error('provider', 'Provider non pris en charge')
        raise errors

    return new_venue_provider


def _connect_allocine_to_venue(venue: VenueSQLEntity, payload: Dict) -> AllocineVenueProvider:
    allocine_theater_id = get_allocine_theaterId_for_venue(venue)
    allocine_venue_provider = _create_allocine_venue_provider(allocine_theater_id, payload, venue)
    allocine_venue_provider_price_rule = _create_allocine_venue_provider_price_rule(allocine_venue_provider, payload.get('price'))

    repository.save(allocine_venue_provider_price_rule)

    return allocine_venue_provider


def _connect_titelive_or_libraires_to_venue(venue: VenueSQLEntity, payload: Dict) -> VenueProvider:
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.providerId = dehumanize(payload['providerId'])
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


def _create_allocine_venue_provider(allocine_theater_id: str, payload: Dict, venue: VenueSQLEntity) -> AllocineVenueProvider:
    allocine_venue_provider = AllocineVenueProvider()
    allocine_venue_provider.venue = venue
    allocine_venue_provider.providerId = dehumanize(payload['providerId'])
    allocine_venue_provider.venueIdAtOfferProvider = allocine_theater_id
    allocine_venue_provider.isDuo = payload.get('isDuo')
    allocine_venue_provider.quantity = payload.get('quantity')

    return allocine_venue_provider

def check_venue_can_be_synchronized_with_libraires(venue: VenueSQLEntity):
    if not are_stocks_available_from_libraires_api(venue.siret):
        errors = ApiErrors()
        errors.status_code = 422
        errors.add_error('provider', f'L’importation d’offres avec LesLibraires n’est pas disponible pour le siret {venue.siret}')
        raise errors
