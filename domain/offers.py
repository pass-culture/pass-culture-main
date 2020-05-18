from typing import List

from local_providers import AllocineStocks
from models import BookingSQLEntity, Offer, UserSQLEntity


def update_is_active_status(offers: List[Offer], status: bool) -> List[Offer]:
    for offer in offers:
        offer.isActive = status

    return offers


def is_from_allocine(offer: Offer) -> bool:
    return offer.isFromProvider and offer.lastProvider.localClass == AllocineStocks.__name__
