from algolia.orchestrator import orchestrate
from models import Offer


def indexing(limit: int = 1) -> None:
    offer_ids = []
    offers = Offer.query.limit(limit)

    for offer in offers:
        offer_ids.append(offer.id)

    orchestrate(offer_ids)
