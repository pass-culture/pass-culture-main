from datetime import datetime

from pcapi.models import SeenOffer
from pcapi.repository import repository, seen_offer_queries


def save_seen_offer(user_id: int, offer_id: int) -> None:
    seen_offer = seen_offer_queries.find_by_offer_id_and_user_id(offer_id, user_id)
    if not seen_offer:
        seen_offer = _create_seen_offer(offer_id, user_id)
    seen_offer.dateSeen = datetime.utcnow()
    repository.save(seen_offer)


def _create_seen_offer(offer_id: int, user_id: int) -> SeenOffer:
    seen_offer = SeenOffer()
    seen_offer.offerId = offer_id
    seen_offer.userId = user_id
    return seen_offer
