from datetime import datetime
from typing import Optional

from models import Offer


class Stock(object):

    def __init__(self,
                 identifier: int,
                 quantity: int,
                 offer: Offer,
                 price: int,
                 beginning_datetime: Optional[datetime] = None,
                 booking_limit_datetime: Optional[datetime] = None):
        self.identifier: int = identifier
        self.quantity: int = quantity
        self.beginningDatetime: datetime = beginning_datetime
        self.offer = offer
        self.price = price
        self.bookingLimitDatetime = booking_limit_datetime
