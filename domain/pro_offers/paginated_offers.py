from typing import List

from models import OfferSQLEntity
from routes.serialization import as_dict
from utils.includes import OFFER_INCLUDES


class PaginatedOffers:
    def __init__(self, offers: List[OfferSQLEntity], total: int):
        self.offers = [as_dict(offer, includes=OFFER_INCLUDES) for offer in offers]
        self.total = total
