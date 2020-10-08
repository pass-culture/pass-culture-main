from typing import List

from pcapi.local_providers import AllocineStocks
from pcapi.models import BookingSQLEntity, OfferSQLEntity, UserSQLEntity


def update_is_active_status(offers: List[OfferSQLEntity], status: bool) -> List[OfferSQLEntity]:
    for offer in offers:
        offer.isActive = status

    return offers


def is_from_allocine(offer: OfferSQLEntity) -> bool:
    return offer.isFromProvider and offer.lastProvider.localClass == AllocineStocks.__name__
