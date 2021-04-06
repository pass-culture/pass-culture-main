from decimal import Decimal

from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import VenueProvider
from pcapi.domain.price_rule import PriceRule
from pcapi.models import AllocineVenueProviderPriceRule
from pcapi.models import Venue
from pcapi.models.allocine_pivot import AllocinePivot
from pcapi.repository import repository
from pcapi.repository.allocine_pivot_queries import get_allocine_pivot_for_venue
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.utils.human_ids import dehumanize


ERROR_CODE_PROVIDER_NOT_SUPPORTED = 400
ERROR_CODE_SIRET_NOT_SUPPORTED = 422


def connect_venue_to_allocine(venue: Venue, venue_provider_payload: PostVenueProviderBody) -> AllocineVenueProvider:
    allocine_pivot = get_allocine_pivot_for_venue(venue)
    venue_provider = _create_allocine_venue_provider(allocine_pivot, venue_provider_payload, venue)
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
    allocine_pivot: AllocinePivot, venue_provider_payload: PostVenueProviderBody, venue: Venue
) -> AllocineVenueProvider:
    allocine_venue_provider = AllocineVenueProvider()
    allocine_venue_provider.venue = venue
    allocine_venue_provider.providerId = dehumanize(venue_provider_payload.providerId)
    allocine_venue_provider.venueIdAtOfferProvider = allocine_pivot.theaterId
    allocine_venue_provider.isDuo = venue_provider_payload.isDuo
    allocine_venue_provider.quantity = venue_provider_payload.quantity
    allocine_venue_provider.internalId = allocine_pivot.internalId

    return allocine_venue_provider
