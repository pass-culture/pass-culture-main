import logging

from pcapi.core.offerers.factories import VenueTypeFactory
from pcapi.core.offerers.models import VenueType
from pcapi.core.offerers.models import VenueTypeCode


logger = logging.getLogger(__name__)


def create_industrial_venue_types() -> list[VenueType]:
    logger.info("create_industrial_venue_types")

    labels = [venue_type.value for venue_type in VenueTypeCode]
    venue_types = [VenueTypeFactory(label=label) for label in labels]

    logger.info("created %i venue types", len(venue_types))

    return venue_types
