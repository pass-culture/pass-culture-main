from typing import List

from pcapi.local_providers import AllocineStocks
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import UserSQLEntity


def update_is_active_status(offers: List[Offer], status: bool) -> List[Offer]:
    for offer in offers:
        offer.isActive = status

    return offers


def is_from_allocine(offer: Offer) -> bool:
    return offer.isFromProvider and offer.lastProvider.localClass == AllocineStocks.__name__
