from pcapi.models import Venue
from pcapi.models import VenueProvider
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.utils.logger import logger

from . import synchronize_fnac_stocks


def synchronize_fnac_venues_stocks() -> None:
    fnac_provider_id = get_provider_by_local_class("FnacStocks").id
    venues = (
        Venue.query.join(VenueProvider)
        .filter(VenueProvider.providerId == fnac_provider_id)
        .filter(VenueProvider.isActive == True)
        .all()
    )

    for venue in venues:
        try:
            synchronize_fnac_stocks.synchronize_venue_stocks_from_fnac(venue)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Could not synchronize stock of venue=%s: %s", venue.id, exc)
