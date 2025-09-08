from typing import Sequence

import factory

from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.models import Venue
from pcapi.core.providers.factories import OffererProviderFactory
from pcapi.core.providers.factories import PublicApiProviderFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.models import Provider


def create_collective_api_provider(venues: Sequence[Venue], api_key_prefix: str | None = None) -> Provider:
    """
    Create Api Key with shape: collective_{offererId}_clear{offererId}
    If api_key_prefix is given, the key will be <api_key_prefix>_clear
    """

    provider = PublicApiProviderFactory.create(name=factory.Sequence("Collective API Provider {}".format))

    for venue in venues:
        VenueProviderFactory.create(venue=venue, provider=provider)

    offerer = venues[0].managingOfferer
    OffererProviderFactory.create(offerer=offerer, provider=provider)

    if api_key_prefix is not None:
        prefix = api_key_prefix
        secret = "clear"
    else:
        prefix = f"collective_{offerer.id}"
        secret = f"clear{offerer.id}"

    ApiKeyFactory.create(offerer=offerer, provider=provider, prefix=prefix, secret=secret)

    return provider
