import os

from flask import current_app as app

from pcapi.algolia.infrastructure.api import clear_index
from pcapi.algolia.usecase.orchestrator import process_eligible_offers
from pcapi.connectors.redis import delete_all_indexed_offers
from pcapi.models import OfferSQLEntity
from pcapi.utils.logger import logger


def create_industrial_algolia_indexed_objects():
    algolia_trigger_indexation = os.environ.get('ALGOLIA_TRIGGER_INDEXATION', '0')

    if algolia_trigger_indexation == '1':
        logger.info('create_industrial_algolia_objects')
        offer_ids = OfferSQLEntity.query.with_entities(OfferSQLEntity.id).all()
        clear_index()
        delete_all_indexed_offers(client=app.redis_client)
        process_eligible_offers(client=app.redis_client, offer_ids=offer_ids, from_provider_update=False)
