from pcapi.models import VenueProvider
from pcapi.models import VenueSQLEntity
from pcapi.repository.provider_queries import get_provider_by_local_class

from . import synchronize_fnac_stocks


def synchronize_fnac_venues_stocks() -> None:
    fnac_provider_id = get_provider_by_local_class("FnacStocks").id
    venues = (
        VenueSQLEntity.query.join(VenueProvider)
        .filter(VenueProvider.providerId == fnac_provider_id)
        .filter(VenueProvider.isActive == True)
        .all()
    )

    for venue in venues:
        synchronize_fnac_stocks.synchronize_venue_stocks_from_fnac(venue)
