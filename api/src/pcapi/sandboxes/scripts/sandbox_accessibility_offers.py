from pcapi.core import search
from pcapi.sandboxes.scripts.getters.native import create_accessibility_offers


def save_sandbox() -> None:
    offers_dict = create_accessibility_offers()
    venue_id = offers_dict["venueId"]
    search.reindex_venue_ids([venue_id])

    offer_ids = [e["id"] for e in offers_dict["offers"]]
    search.reindex_offer_ids(offer_ids)
