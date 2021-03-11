from pcapi.models import VenueProvider
from pcapi.models.provider import Provider
from pcapi.utils.logger import logger

from . import synchronize_provider_api


def synchronize_stocks() -> None:
    venue_providers = (
        VenueProvider.join(Provider).filter(Provider.apiUrl != None).filter(VenueProvider.isActive == True).all()
    )

    for venue_provider in venue_providers:
        try:
            synchronize_provider_api.synchronize_venue_provider(venue_provider)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Could not synchronize venue_provider=%s: %s", venue_provider.id, exc)
