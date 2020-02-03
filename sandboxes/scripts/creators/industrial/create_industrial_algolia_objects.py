import os

from flask import current_app as app

from algolia.api import clean_algolia_index
from algolia.orchestrator import process_eligible_offers
from models import Offer
from utils.logger import logger


def create_industrial_algolia_indexed_objects():
    algolia_trigger_indexation = os.environ.get('ALGOLIA_TRIGGER_INDEXATION', False)
    if algolia_trigger_indexation:
        logger.info('create_industrial_algolia_objects')
        offer_ids = Offer.query.with_entities(Offer.id).all()
        clean_algolia_index()
        process_eligible_offers(client=app.redis_client, offer_ids=offer_ids, from_provider_update=False)
