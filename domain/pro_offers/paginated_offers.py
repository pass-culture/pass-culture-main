from typing import List

from models import OfferSQLEntity


class PaginatedOffers:
    def __init__(self, offers: List[OfferSQLEntity], total: int):
        self.offers = offers
        self.total = total
