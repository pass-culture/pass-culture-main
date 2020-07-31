from datetime import datetime
from typing import Optional


class Stock(object):
    def __init__(self,
                 id: int,
                 quantity: Optional[int],
                 offerId: int,
                 price: float,
                 dateCreated: datetime,
                 dateModified: datetime,
                 isSoftDeleted: bool,
                 isOfferActive: bool,
                 remainingQuantity: Optional[int],
                 beginningDatetime: Optional[datetime] = None,
                 bookingLimitDatetime: Optional[datetime] = None,
                 ):
        self.isOfferActive = isOfferActive
        self.isSoftDeleted = isSoftDeleted
        self.remainingQuantity = remainingQuantity
        self.id = id
        self.bookingLimitDatetime = bookingLimitDatetime
        self.beginningDatetime = beginningDatetime
        self.dateModified = dateModified
        self.dateCreated = dateCreated
        self.quantity = quantity
        self.offerId = offerId
        self.price = price

    @property
    def is_event_expired(self) -> bool:
        if not self.beginningDatetime:
            return False
        return self.beginningDatetime <= datetime.utcnow()

    @property
    def has_booking_limit_datetime_passed(self):
        if self.bookingLimitDatetime and self.bookingLimitDatetime < datetime.utcnow():
            return True
        return False

    @property
    def is_bookable(self) -> bool:
        if self.has_booking_limit_datetime_passed:
            return False
        if not self.isOfferActive:
            return False
        if self.isSoftDeleted:
            return False
        if self.beginningDatetime and self.beginningDatetime < datetime.utcnow():
            return False
        if self.quantity is not None and self.remainingQuantity == 0:
            return False
        return True
