from decimal import Decimal
from typing import Callable, Dict

from domain.price_rule import PriceRule
from models import AllocineVenueProvider, AllocineVenueProviderPriceRule, VenueProvider, VenueSQLEntity
from repository import repository
from repository.allocine_pivot_queries import get_allocine_theaterId_for_venue
from utils.human_ids import dehumanize
from validation.routes.venues import check_existing_venue

ERROR_CODE_PROVIDER_NOT_SUPPORTED = 400
ERROR_CODE_SIRET_NOT_SUPPORTED = 422


def connect_allocine_to_venue(venue_provider_payload: Dict,
                              find_by_id: Callable) -> AllocineVenueProvider:
    venue_id = dehumanize(venue_provider_payload['venueId'])
    venue = find_by_id(venue_id)
    check_existing_venue(venue)

    theater_id = get_allocine_theaterId_for_venue(venue)
    venue_provider = _create_allocine_venue_provider(theater_id, venue_provider_payload, venue)
    venue_provider_price_rule = _create_allocine_venue_provider_price_rule(venue_provider,
                                                                           venue_provider_payload.get('price'))

    repository.save(venue_provider_price_rule)

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
