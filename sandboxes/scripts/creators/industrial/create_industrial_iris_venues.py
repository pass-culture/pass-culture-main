from scripts.iris.link_iris_to_venues import link_irises_to_existing_physical_venues
from utils.logger import logger


def create_industrial_iris_venues():
    link_irises_to_existing_physical_venues()

    logger.info('irises linked to venues'.format())
