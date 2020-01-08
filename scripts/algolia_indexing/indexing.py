from algolia.orchestrator import orchestrate
from connectors.redis import get_offer_ids, delete_offer_ids
from models import Offer


def indexing(limit: int = 1) -> None:
    offer_ids = []
    offers = Offer.query.limit(limit)

    for offer in offers:
        offer_ids.append(offer.id)

    orchestrate(offer_ids)


def index_offers() -> None:
    offer_ids = get_offer_ids()
    orchestrate(offer_ids)
    delete_offer_ids()
