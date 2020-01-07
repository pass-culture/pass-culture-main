import os

from algolia.orchestrator import orchestrate
from models import Offer
from utils.logger import logger


def create_industrial_algolia_indexed_objects():
    algolia_allow_indexation = True if os.environ.get('ALGOLIA_TRIGGER_INDEXATION') else False

    if algolia_allow_indexation is True:
        logger.info('create_industrial_algolia_objects')
        offer_ids = Offer.query.with_entities(Offer.id).all()
        orchestrate(offer_ids)

