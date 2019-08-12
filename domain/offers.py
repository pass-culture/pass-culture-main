from typing import List

from models import Offer


class InconsistentOffer(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


def update_is_active_status(offers: List[Offer], status: bool) -> List[Offer]:
    for offer in offers:
        offer.isActive = status

    return offers
