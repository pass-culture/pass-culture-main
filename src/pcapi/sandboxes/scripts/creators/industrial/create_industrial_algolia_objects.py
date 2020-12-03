from flask import current_app as app

from pcapi import settings
from pcapi.algolia.infrastructure.api import clear_index
from pcapi.algolia.usecase.orchestrator import process_eligible_offers
from pcapi.connectors.redis import delete_all_indexed_offers
from pcapi.models import Offer
from pcapi.utils.logger import logger


def create_industrial_algolia_indexed_objects() -> None:
    if settings.ALGOLIA_TRIGGER_INDEXATION:
        logger.info("create_industrial_algolia_objects")
        offer_ids = Offer.query.with_entities(Offer.id).all()
        clear_index()
        delete_all_indexed_offers(client=app.redis_client)
        process_eligible_offers(client=app.redis_client, offer_ids=offer_ids, from_provider_update=False)
