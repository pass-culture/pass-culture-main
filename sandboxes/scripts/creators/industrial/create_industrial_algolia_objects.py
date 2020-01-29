import os

from algolia.orchestrator import orchestrate_from_offer
from models import Offer
from utils.logger import logger


def create_industrial_algolia_indexed_objects():
    algolia_trigger_indexation = os.environ.get('ALGOLIA_TRIGGER_INDEXATION', False)

    if algolia_trigger_indexation:
        logger.info('create_industrial_algolia_objects')
        offer_ids = Offer.query.with_entities(Offer.id).all()
        orchestrate_from_offer(offer_ids, True)
