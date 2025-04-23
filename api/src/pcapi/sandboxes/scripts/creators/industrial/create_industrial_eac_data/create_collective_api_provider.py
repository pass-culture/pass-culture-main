from typing import Sequence

import factory

from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.models import Venue
from pcapi.core.providers.factories import OffererProviderFactory
from pcapi.core.providers.factories import PublicApiProviderFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.models import Provider


def create_collective_api_provider(venues: Sequence[Venue]) -> Provider:
    "Create api_keys with shape : collective_{offererId}_clear{offererId}"

    provider = PublicApiProviderFactory.create(name=factory.Sequence("Collective API Provider {}".format))

    for venue in venues:
        VenueProviderFactory.create(venue=venue, provider=provider)

    offerer = venues[0].managingOfferer
    OffererProviderFactory.create(offerer=offerer, provider=provider)
    ApiKeyFactory.create(
        offerer=offerer, provider=provider, prefix=f"collective_{offerer.id}", secret=f"clear{offerer.id}"
    )

    return provider
