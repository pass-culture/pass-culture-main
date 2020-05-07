from datetime import datetime

from domain.stock.stock import Stock
from domain.user.user import User


class Booking(object):
    def __init__(self,
                 user: User,
                 stock: Stock,
                 amount: float,
                 quantity: int,
                 recommendation_id: int = None,
                 is_cancelled: bool = False,
                 identifier: int = None,
                 token: str = None,
                 date_booked: datetime = datetime.utcnow()):
        self.identifier = identifier
        self.user = user
        self.stock = stock
        self.amount = amount
        self.quantity = quantity
        self.isCancelled = is_cancelled
        self.recommendation_id = recommendation_id
        self.token = token
        self.dateCreated = date_booked

    @property
    def total_amount(self) -> float:
        return self.amount * self.quantity
