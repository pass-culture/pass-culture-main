from datetime import datetime

from domain.stock.stock import Stock
from domain.beneficiary.beneficiary import Beneficiary
from utils.human_ids import humanize


class Booking(object):
    def __init__(self,
                 beneficiary: Beneficiary,
                 stock: Stock,
                 amount: float,
                 quantity: int,
                 recommendation_id: int = None,
                 is_cancelled: bool = False,
                 is_used: bool = False,
                 identifier: int = None,
                 token: str = None,
                 date_booked: datetime = datetime.utcnow()):
        self.identifier = identifier
        self.beneficiary = beneficiary
        self.stock = stock
        self.amount = amount
        self.quantity = quantity
        self.isCancelled = is_cancelled
        self.is_used = is_used
        self.recommendation_id = recommendation_id
        self.token = token
        self.dateCreated = date_booked

    @property
    def total_amount(self) -> float:
        return self.amount * self.quantity

    @property
    def completed_url(self):
        url = self.stock.offer.url
        if url is None:
            return None
        if not url.startswith('http'):
            url = "http://" + url
        return url.replace('{token}', self.token) \
            .replace('{offerId}', humanize(self.stock.offer.id)) \
            .replace('{email}', self.beneficiary.email)
