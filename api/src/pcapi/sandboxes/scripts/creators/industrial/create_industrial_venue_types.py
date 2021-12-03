import logging

from pcapi.core.offerers.factories import VenueTypeFactory
from pcapi.core.offerers.models import VENUE_TYPE_CODE_MAPPING
from pcapi.core.offerers.models import VenueType


logger = logging.getLogger(__name__)


def create_industrial_venue_types() -> list[VenueType]:
    logger.info("create_industrial_venue_types")

    labels = VENUE_TYPE_CODE_MAPPING.values()
    venue_types = [VenueTypeFactory(label=label) for label in labels]

    logger.info("created %i venue types", len(venue_types))

    return venue_types
