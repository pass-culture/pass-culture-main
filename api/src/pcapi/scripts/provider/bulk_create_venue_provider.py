# This script is used to automatically create venue_provider from
# an existing provider and multiple venues

from pcapi.core.offerers import models as offerer_models
from pcapi.core.providers import api as provider_api
from pcapi.core.providers import models as provider_models
from pcapi.models import db


def create_venue_provider(provider_id: int, venue_ids: list[int]) -> None:
    provider = provider_models.Provider.query.filter_by(provider_id).one_or_none()
    if not provider or not provider.hasOffererProvider:
        print("Provider not found or not synchronisable")
        return

    venues = (
        db.session.query(provider_models.Venue)
        .outerjoin(provider_models.VenueProvider)
        .filter(offerer_models.Venue.id.in_(venue_ids))
        .all()
    )

    missing = set(venue_ids) - {venue.id for venue in venues}
    if missing:
        print(f"Some venues were not found: {missing}")
        return

    for venue in venues:
        if len(venue.venueProviders):
            print(f"Venue {venue.id} already linked to a provider")
            continue
        provider_api.connect_venue_to_provider(venue, provider, venueIdAtOfferProvider=None)
        print(f"Venue <#{venue.id} {venue.name}> linked to provider <#{provider.id} {provider.name}>")
