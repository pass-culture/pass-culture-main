import base64
import logging

from sqlalchemy.orm.util import aliased

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.models import db
from pcapi.models.allocine_pivot import AllocinePivot


logger = logging.getLogger(__name__)


def add_allocine_internal_ids() -> None:
    logger.info("Starting to update allocine pivots internal id")

    # Approx 900 rows so no performance issue to select all
    allocine_pivots: list[AllocinePivot] = AllocinePivot.query.all()
    logger.info("%d allocine pivots found", len(allocine_pivots))

    for allocine_pivot in allocine_pivots:
        decoded_id = base64.b64decode(allocine_pivot.theaterId).decode("ascii")
        internal_id = decoded_id.split("Theater:")[1]
        allocine_pivot.internalId = internal_id

    db.session.bulk_save_objects(allocine_pivots)
    db.session.commit()
    logger.info("Allocine pivots have been updated")

    logger.info("Starting to update allocine venue providers internal id")

    # Approx 48 rows so no performance issue to select all
    venue_alias = aliased(Venue)
    allocine_venue_providers_with_pivot: list[tuple[AllocineVenueProvider, AllocinePivot]] = (
        AllocineVenueProvider.query.join(venue_alias, venue_alias.id == AllocineVenueProvider.venueId)
        .join(AllocinePivot, AllocinePivot.siret == venue_alias.siret)
        .with_entities(AllocineVenueProvider, AllocinePivot)
        .all()
    )

    logger.info("%d allocine venue providers found", len(allocine_venue_providers_with_pivot))
    for allocine_venue_provider, allocine_pivot in allocine_venue_providers_with_pivot:
        allocine_venue_provider.internalId = allocine_pivot.internalId

    db.session.bulk_save_objects(
        [allocine_venue_provider for allocine_venue_provider, _unused in allocine_venue_providers_with_pivot]
    )
    db.session.commit()
    logger.info("Allocine venue providers have been updated")
