from datetime import datetime, timedelta
from typing import List

from sqlalchemy import or_

from models import VenueProvider


def get_venue_providers_to_sync(provider_id: int) -> List[VenueProvider]:
    last_sync_happened_more_than_24_hours_ago = VenueProvider.lastSyncDate < (datetime.utcnow() - timedelta(days=1))
    return VenueProvider.query \
        .filter(VenueProvider.providerId == provider_id) \
        .filter(or_(VenueProvider.lastSyncDate == None,
                    last_sync_happened_more_than_24_hours_ago)) \
        .filter(VenueProvider.syncWorkerId == None) \
        .all()


def get_nb_containers_at_work() -> int:
    return VenueProvider.query \
        .filter(VenueProvider.syncWorkerId != None) \
        .count()
