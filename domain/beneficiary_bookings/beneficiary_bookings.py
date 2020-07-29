from datetime import datetime
from typing import List, Optional, Dict

from utils.human_ids import humanize


class BeneficiaryBooking:
    def __init__(self,
                 amount: int,
                 cancellationDate: datetime,
                 dateCreated: datetime,
                 dateUsed: datetime,
                 id: int,
                 isCancelled: bool,
                 isUsed: bool,
                 quantity: int,
                 recommendationId: int,
                 stockId: int,
                 token: str,
                 userId: int,
                 offerId: int,
                 name: str,
                 type: str,
                 url: Optional[str],
                 email: str,
                 beginningDatetime: datetime,
                 venueId: int,
                 departementCode: str,
                 ):
        self.amount = amount
        self.cancellationDate = cancellationDate
        self.dateCreated = dateCreated
        self.dateUsed = dateUsed
        self.id = id
        self.isCancelled = isCancelled
        self.isUsed = isUsed
        self.quantity = quantity
        self.recommendationId = recommendationId
        self.stockId = stockId
        self.token = token
        self.userId = userId
        self.offerId = offerId
        self.name = name
        self.type = type
        self.url = url
        self.email = email
        self.beginningDatetime = beginningDatetime
        self.venueId = venueId
        self.departementCode = departementCode

    @property
    def beneficiary_offer_access_url(self):
        url = self.url
        if url is None:
            return None
        if not url.startswith('http'):
            url = "http://" + url
        return url.replace('{token}', self.token) \
            .replace('{offerId}', humanize(self.offerId)) \
            .replace('{email}', self.email)

    @property
    def is_event_expired(self):
        if not self.beginningDatetime:
            return False
        return self.beginningDatetime <= datetime.utcnow()


class BeneficiaryBookings:
    def __init__(self, bookings: List[BeneficiaryBooking], stocks: List[Dict]):
        self.bookings = bookings
        self.stocks = stocks
