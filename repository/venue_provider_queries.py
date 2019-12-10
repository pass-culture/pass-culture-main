from datetime import datetime, timedelta
from typing import List

from sqlalchemy import or_

from models import VenueProvider


def get_venue_providers_to_sync(provider_id: int) -> List[VenueProvider]:
    return VenueProvider.query \
        .filter(VenueProvider.providerId == provider_id) \
        .filter(or_(VenueProvider.lastSyncDate == None,
                    VenueProvider.lastSyncDate < (datetime.utcnow() - timedelta(days=1)))) \
        .filter(VenueProvider.syncWorkerId == None) \
        .all()
