from flask import current_app as app

from pcapi.connectors import redis
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueType
from pcapi.domain.iris import link_valid_venue_to_irises
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository.iris_venues_queries import delete_venue_from_iris_venues
from pcapi.routes.serialization.venues_serialize import PostVenueBodyModel

from . import validation


UNCHANGED = object()
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "city"]


def create_digital_venue(offerer):
    digital_venue = Venue()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeId = _get_digital_venue_type_id()
    digital_venue.managingOfferer = offerer
    return digital_venue


def _get_digital_venue_type_id() -> int:
    return VenueType.query.filter_by(label="Offre numérique").one().id


def update_venue(
    venue: Venue,
    address: str = UNCHANGED,
    name: str = UNCHANGED,
    siret: str = UNCHANGED,
    latitude: float = UNCHANGED,
    longitude: float = UNCHANGED,
    bookingEmail: str = UNCHANGED,
    postalCode: str = UNCHANGED,
    city: str = UNCHANGED,
    publicName: str = UNCHANGED,
    comment: str = UNCHANGED,
    venueTypeId: int = UNCHANGED,
    venueLabelId: int = UNCHANGED,
) -> Venue:
    validation.validate_coordinates(
        latitude if latitude is not UNCHANGED else None,
        longitude if latitude is not UNCHANGED else None,
    )

    # fmt: off
    modifications = {
        field: new_value
        for field, new_value in locals().items()
        if field != 'venue'
        and new_value is not UNCHANGED  # has the user provided a value for this field
        and getattr(venue, field) != new_value  # is the value different from what we have on database?
    }
    # fmt: on
    if not modifications:
        return venue

    validation.check_venue_edition(modifications, venue)
    venue.populate_from_dict(modifications)

    if not venue.isVirtual:
        delete_venue_from_iris_venues(venue.id)

    repository.save(venue)

    link_valid_venue_to_irises(venue)

    indexing_modifications_fields = set(modifications.keys()) & set(VENUE_ALGOLIA_INDEXED_FIELDS)

    if indexing_modifications_fields:
        if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
            redis.add_venue_id(client=app.redis_client, venue_id=venue.id)

    return venue


def create_venue(venue_data: PostVenueBodyModel) -> Venue:
    data = venue_data.dict(by_alias=True)
    venue = Venue()
    venue.populate_from_dict(data)

    repository.save(venue)

    link_valid_venue_to_irises(venue=venue)

    return venue
