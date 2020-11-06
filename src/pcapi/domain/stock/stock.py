from datetime import datetime
from typing import Optional, List

from pcapi.models import Booking
from pcapi.models import Offer


class Stock(object):
    def __init__(self,
                 identifier: int,
                 quantity: Optional[int],
                 offer: Offer,
                 price: float,
                 beginning_datetime: Optional[datetime] = None,
                 booking_limit_datetime: Optional[datetime] = None,
                 is_soft_deleted: bool = False,
                 bookings: List[Booking] = []):
        self.identifier = identifier
        self.quantity = quantity
        self.beginningDatetime: datetime = beginning_datetime
        self.offer = offer
        self.price = price
        self.bookingLimitDatetime = booking_limit_datetime
        self.is_soft_deleted = is_soft_deleted
        self.bookings = bookings

    def has_booking_limit_datetime_passed(self):
        if self.bookingLimitDatetime and self.bookingLimitDatetime < datetime.utcnow():
            return True
        return False

    def bookings_quantity(self):
        return sum([booking.quantity for booking in self.bookings if not booking.isCancelled])

    def remaining_quantity(self):
        return 'unlimited' if self.quantity is None else self.quantity - self.bookings_quantity()

    def is_bookable(self):
        if self.has_booking_limit_datetime_passed():
            return False
        if not self.offer.venue.managingOfferer.isActive:
            return False
        if self.offer.venue.managingOfferer.validationToken:
            return False
        if self.offer.venue.validationToken:
            return False
        if not self.offer.isActive:
            return False
        if self.is_soft_deleted:
            return False
        if self.beginningDatetime and self.beginningDatetime < datetime.utcnow():
            return False
        if self.quantity is not None and self.remaining_quantity() == 0:
            return False
        return True
