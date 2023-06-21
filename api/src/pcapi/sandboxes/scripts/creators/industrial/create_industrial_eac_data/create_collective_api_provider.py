from typing import Sequence

import factory

from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.models import Venue
from pcapi.core.providers.factories import APIProviderFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.models import Provider


def create_collective_api_provider(venues: Sequence[Venue]) -> Provider:
    provider = APIProviderFactory(name=factory.Sequence("Collectie API Provider {}".format))

    for venue in venues:
        VenueProviderFactory(venue=venue, provider=provider)

    offerer = venues[0].managingOfferer
    ApiKeyFactory.create(offerer=offerer, provider=provider, prefix=f"collective_api_prefix_for_{provider.id}")

    return provider
