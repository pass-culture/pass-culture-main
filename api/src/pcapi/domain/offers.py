from pcapi.models import Offer


def update_is_active_status(offers: list[Offer], status: bool) -> list[Offer]:
    for offer in offers:
        offer.isActive = status

    return offers
