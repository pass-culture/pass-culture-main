from pcapi.domain.iris import MAXIMUM_DISTANCE_IN_METERS
from pcapi.scripts.iris.link_iris_to_venues import link_irises_to_existing_physical_venues
from pcapi.utils.logger import logger


def create_industrial_iris_venues():
    link_irises_to_existing_physical_venues(MAXIMUM_DISTANCE_IN_METERS)

    logger.info('irises linked to venues')
