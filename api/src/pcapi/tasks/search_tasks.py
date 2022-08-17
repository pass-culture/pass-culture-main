import logging

from pcapi import settings
from pcapi.core import search
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.decorator import task
from pcapi.utils.chunks import get_chunks


logger = logging.getLogger(__name__)


class IndexOffersRequest(BaseModel):
    start_id: int
    batch_size: int
    total: int


@task(settings.GCP_SEARCH_REINDEX_QUEUE_NAME, "/search/reindex/offers")
def reindex_offers_batch(payload: IndexOffersRequest) -> None:
    offer_ids = list(range(payload.start_id, payload.start_id + payload.total))
    for offer_ids_chunk in get_chunks(offer_ids, payload.batch_size):
        search.reindex_offer_ids(offer_ids_chunk)
        logger.info("Reindexed offers: from %d to %d", offer_ids_chunk[0], offer_ids_chunk[-1])
