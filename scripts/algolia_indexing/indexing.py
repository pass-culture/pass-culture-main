from redis import Redis

from algolia.orchestrator import orchestrate
from connectors.redis import get_offer_ids, delete_offer_ids
from models import Offer


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
