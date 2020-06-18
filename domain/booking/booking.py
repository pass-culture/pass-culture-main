from datetime import datetime, timedelta
from typing import Optional

from domain.beneficiary.beneficiary import Beneficiary
from domain.booking.booking_exceptions import BookingIsAlreadyUsed, EventHappensInLessThan72Hours
from domain.stock.stock import Stock
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
    def completed_url(self) -> Optional[str]:
        url = self.stock.offer.url
        if url is None:
            return None
        if not url.startswith('http'):
            url = "http://" + url
        return url.replace('{token}', self.token) \
            .replace('{offerId}', humanize(self.stock.offer.id)) \
            .replace('{email}', self.beneficiary.email)

    def cancel(self) -> None:
        if self.is_used:
            raise BookingIsAlreadyUsed()
        is_event_stock = self.stock.beginningDatetime is not None
        is_stock_in_less_than_72_hours = is_event_stock and self.stock.beginningDatetime < datetime.utcnow() + timedelta(
            hours=72)
        if is_stock_in_less_than_72_hours:
            raise EventHappensInLessThan72Hours()
        self.isCancelled = True
