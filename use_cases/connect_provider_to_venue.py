from decimal import Decimal
from typing import Dict

from local_providers import AllocineStocks, LibrairesStocks, TiteLiveStocks
from local_providers.local_provider import LocalProvider
from local_providers.price_rule import PriceRule
from models import AllocineVenueProvider, Venue, VenueProvider, AllocineVenueProviderPriceRule
from repository import repository
from repository.allocine_pivot_queries import get_allocine_theaterId_for_venue
from utils.human_ids import dehumanize
from utils.rest import load_or_404


def connect_provider_to_venue(provider_type: LocalProvider, venue_provider_payload: Dict) -> VenueProvider:
    venue = load_or_404(Venue, venue_provider_payload['venueId'])
    if provider_type == AllocineStocks:
        new_venue_provider = _connect_allocine_to_venue(venue, venue_provider_payload)
    elif provider_type == LibrairesStocks or TiteLiveStocks:
        new_venue_provider = _connect_titelive_or_libraires_to_venue(venue, venue_provider_payload)

    return new_venue_provider


def _connect_allocine_to_venue(venue: Venue, payload: Dict) -> AllocineVenueProvider:
    allocine_theater_id = get_allocine_theaterId_for_venue(venue)

    allocine_venue_provider = _create_allocine_venue_provider(allocine_theater_id, payload, venue)

    venue_provider_price_rule = _create_venue_provider_price_rule(allocine_venue_provider, payload.get('price'))

    repository.save(venue_provider_price_rule)

    return allocine_venue_provider


def _connect_titelive_or_libraires_to_venue(venue: Venue, payload: Dict) -> VenueProvider:
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.providerId = dehumanize(payload['providerId'])
    venue_provider.venueIdAtOfferProvider = venue.siret

    repository.save(venue_provider)
    return venue_provider


def _create_venue_provider_price_rule(allocine_venue_provider: VenueProvider, price: Decimal) -> AllocineVenueProviderPriceRule:
    venue_provider_price_rule = AllocineVenueProviderPriceRule()
    venue_provider_price_rule.allocineVenueProvider = allocine_venue_provider
    venue_provider_price_rule.priceRule = PriceRule.default
    venue_provider_price_rule.price = price

    return venue_provider_price_rule


def _create_allocine_venue_provider(allocine_theater_id: str, payload: Dict, venue: Venue) -> AllocineVenueProvider:
    allocine_venue_provider = AllocineVenueProvider()
    allocine_venue_provider.venue = venue
    allocine_venue_provider.providerId = dehumanize(payload['providerId'])
    allocine_venue_provider.venueIdAtOfferProvider = allocine_theater_id
    allocine_venue_provider.isDuo = payload.get('isDuo')
    allocine_venue_provider.available = payload.get('available')

    return allocine_venue_provider


