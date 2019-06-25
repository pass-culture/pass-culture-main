from typing import Optional

from models import VenueProvider
from utils.human_ids import dehumanize


def find_venue_provider(provider_id: int, venue_id: int, venue_id_at_offer_provider: str) -> Optional[VenueProvider]:
    return VenueProvider.query.filter_by(
        providerId=provider_id,
        venueId=venue_id,
        venueIdAtOfferProvider=venue_id_at_offer_provider
    ).first()
