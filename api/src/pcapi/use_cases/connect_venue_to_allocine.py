from decimal import Decimal

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.exceptions import NoPriceSpecified
from pcapi.core.providers.models import AllocinePivot
from pcapi.core.providers.models import AllocineTheater
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.models import VenueProviderCreationPayload
from pcapi.core.providers.repository import AllocineVenue
from pcapi.domain.price_rule import PriceRule
from pcapi.repository import repository


def connect_venue_to_allocine(
    venue: Venue, provider_id: int, venue_provider_payload: VenueProviderCreationPayload
) -> AllocineVenueProvider:

    allocine_venue = AllocineVenue(venue=venue)

    if not venue_provider_payload.price:
        raise NoPriceSpecified()

    if not allocine_venue.has_pivot():
        allocine_pivot = _create_allocine_pivot_for_venue(allocine_venue.get_theater(), venue)
        allocine_venue.allocine_pivot = allocine_pivot
        repository.save(allocine_pivot)

    venue_provider = _create_allocine_venue_provider(
        allocine_venue.get_pivot(), provider_id, venue_provider_payload, venue
    )
    venue_provider_price_rule = _create_allocine_venue_provider_price_rule(venue_provider, venue_provider_payload.price)  # type: ignore [arg-type]

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


def _create_allocine_pivot_for_venue(allocine_theater: AllocineTheater, venue: Venue) -> AllocinePivot:
    allocine_pivot = AllocinePivot()
    allocine_pivot.venue = venue
    allocine_pivot.theaterId = allocine_theater.theaterId
    allocine_pivot.internalId = allocine_theater.internalId

    return allocine_pivot
