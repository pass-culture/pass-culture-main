from decimal import Decimal

from pcapi.core.providers.api import VenueProviderCreationPayload
from pcapi.core.providers.exceptions import NoAllocinePivot
from pcapi.core.providers.exceptions import NoPriceSpecified
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import VenueProvider
from pcapi.domain.price_rule import PriceRule
from pcapi.models import Venue
from pcapi.models.allocine_pivot import AllocinePivot
from pcapi.repository import repository
from pcapi.repository.allocine_pivot_queries import get_allocine_pivot_for_venue


ERROR_CODE_PROVIDER_NOT_SUPPORTED = 400
ERROR_CODE_SIRET_NOT_SUPPORTED = 422


def connect_venue_to_allocine(
    venue: Venue, provider_id: int, venue_provider_payload: VenueProviderCreationPayload
) -> AllocineVenueProvider:
    allocine_pivot = get_allocine_pivot_for_venue(venue)

    if not allocine_pivot:
        raise NoAllocinePivot()
    if not venue_provider_payload.price:
        raise NoPriceSpecified()

    venue_provider = _create_allocine_venue_provider(allocine_pivot, provider_id, venue_provider_payload, venue)
    venue_provider_price_rule = _create_allocine_venue_provider_price_rule(venue_provider, venue_provider_payload.price)

    repository.save(venue_provider_price_rule)

    return venue_provider


def _create_allocine_venue_provider_price_rule(
    allocine_venue_provider: VenueProvider, price: Decimal
) -> AllocineVenueProviderPriceRule:
    venue_provider_price_rule = AllocineVenueProviderPriceRule()
    venue_provider_price_rule.allocineVenueProvider = allocine_venue_provider
    venue_provider_price_rule.priceRule = PriceRule.default
    venue_provider_price_rule.price = price

    return venue_provider_price_rule


def _create_allocine_venue_provider(
    allocine_pivot: AllocinePivot, provider_id: int, venue_provider_payload: VenueProviderCreationPayload, venue: Venue
) -> AllocineVenueProvider:
    allocine_venue_provider = AllocineVenueProvider()
    allocine_venue_provider.venue = venue
    allocine_venue_provider.providerId = provider_id
    allocine_venue_provider.venueIdAtOfferProvider = allocine_pivot.theaterId
    allocine_venue_provider.isDuo = venue_provider_payload.isDuo
    allocine_venue_provider.quantity = venue_provider_payload.quantity
    allocine_venue_provider.internalId = allocine_pivot.internalId

    return allocine_venue_provider
