from domain.stock.stock import Stock
from domain.user.user import User


class Booking(object):
    def __init__(self, user: User, stock: Stock, amount: float, quantity: int, is_cancelled: bool = False, identifier: int = None):
        self.identifier = identifier
        self.user = user
        self.stock = stock
        self.amount = amount
        self.quantity = quantity
        self.isCancelled = is_cancelled

    def total_amount(self) -> float:
        return self.amount * self.quantity
