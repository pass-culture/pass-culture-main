from pcapi.core.offerers.repository import find_venue_by_id
from pcapi.repository import repository
from pcapi.repository.offer_queries import get_offers_by_venue_id
from pcapi.utils.human_ids import dehumanize


def delete_venue_and_offers_for_venue_id(humanized_venue_id: str):
    dehumanized_venue_id = dehumanize(humanized_venue_id)
    offers = get_offers_by_venue_id(dehumanized_venue_id)
    venue = find_venue_by_id(dehumanized_venue_id)

    if any(offer.stocks for offer in offers):
        raise AttributeError("Offres non supprimables car au moins une contient des stocks")

    for offer in offers:
        repository.delete(offer)

    if venue:
        repository.delete(venue)
