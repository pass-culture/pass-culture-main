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
                 beginningDatetime: Optional[datetime] = None,
                 bookingLimitDatetime: Optional[datetime] = None,
                 ):
        self.is_offer_active = isOfferActive
        self.is_soft_deleted = isSoftDeleted
        self.id = id
        self.booking_limit_datetime = bookingLimitDatetime
        self.beginning_datetime = beginningDatetime
        self.date_modified = dateModified
        self.date_created = dateCreated
        self.quantity = quantity
        self.offer_id = offerId
        self.price = price

    @property
    def is_event_expired(self) -> bool:
        if not self.beginning_datetime:
            return False
        return self.beginning_datetime <= datetime.utcnow()

    @property
    def has_booking_limit_datetime_passed(self) -> bool:
        if self.booking_limit_datetime and self.booking_limit_datetime < datetime.utcnow():
            return True
        return False

    @property
    def is_available_for_booking(self) -> bool:
        if self.has_booking_limit_datetime_passed:
            return False
        if not self.is_offer_active:
            return False
        if self.is_soft_deleted:
            return False
        if self.is_event_expired:
            return False
        return True
