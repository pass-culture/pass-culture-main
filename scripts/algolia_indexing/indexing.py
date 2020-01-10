from redis import Redis

from algolia.orchestrator import orchestrate
from connectors.redis import get_offer_ids, delete_offer_ids
from models import Offer
from utils.logger import logger


def indexing(limit: int = 1) -> None:
    offer_ids = []
    offers = Offer.query.limit(limit)

    for offer in offers:
        offer_ids.append(offer.id)

    orchestrate(offer_ids)


def indexing_offers_in_algolia(client: Redis) -> None:
    offer_ids = get_offer_ids(client=client)
    orchestrate(offer_ids)
    delete_offer_ids(client=client)


def batch_indexing_offers(limit: int = 10000) -> None:
    page = 0
    has_still_elements = True

    while has_still_elements:
        offer_ids = Offer.query \
            .with_entities(Offer.id) \
            .offset(page * limit) \
            .limit(limit) \
            .all()

        if len(offer_ids) > 0:
            logger.info(f'[ALGOLIA] Indexing offers from page {page}...')
            orchestrate(offer_ids)
        else:
            has_still_elements = False
            logger.info('[ALGOLIA] Indexing offers finished!')
        page += 1
