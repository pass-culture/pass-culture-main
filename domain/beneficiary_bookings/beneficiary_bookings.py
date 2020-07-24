from datetime import datetime
from typing import List, Optional, Dict

from domain.beneficiary_bookings.stock import Stock
from domain.bookings import generate_qr_code
from models.offer_type import ProductType, ThingType, EventType
from utils.human_ids import humanize


class BeneficiaryBooking:
    def __init__(self,
                 amount: int,
                 cancellationDate: Optional[datetime],
                 dateCreated: datetime,
                 dateUsed: Optional[datetime],
                 id: int,
                 isCancelled: bool,
                 isUsed: bool,
                 quantity: int,
                 recommendationId: Optional[int],
                 stockId: int,
                 token: str,
                 userId: int,
                 offerId: int,
                 name: str,
                 type: str,
                 url: Optional[str],
                 email: str,
                 beginningDatetime: Optional[datetime],
                 venueId: int,
                 departementCode: str,
                 description: str,
                 durationMinutes: int,
                 extraData: Dict,
                 isDuo: bool,
                 withdrawalDetails: Optional[str],
                 mediaUrls: List[str],
                 isNational: bool,
                 venueName: str,
                 address: str,
                 postalCode: str,
                 city: str,
                 latitude: float,
                 longitude: float,
                 price: float
                 ):
        self.price = price
        self.longitude = longitude
        self.latitude = latitude
        self.city = city
        self.postalCode = postalCode
        self.address = address
        self.venueName = venueName
        self.isNational = isNational
        self.mediaUrls = mediaUrls
        self.withdrawalDetails = withdrawalDetails
        self.isDuo = isDuo
        self.extraData = extraData
        self.durationMinutes = durationMinutes
        self.description = description
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
    def booking_access_url(self) -> Optional[str]:
        url = self.url
        if url is None:
            return None
        if not url.startswith('http'):
            url = "http://" + url
        return url.replace('{token}', self.token) \
            .replace('{offerId}', humanize(self.offerId)) \
            .replace('{email}', self.email)

    @property
    def is_event_expired(self) -> bool:
        if not self.beginningDatetime:
            return False
        return self.beginningDatetime <= datetime.utcnow()

    @property
    def is_booked_offer_digital(self) -> bool:
        return self.url is not None and self.url != ''

    @property
    def is_booked_offer_event(self) -> bool:
        return ProductType.is_event(self.type)

    @property
    def humanized_offer_type(self) -> str:
        all_types = list(ThingType) + list(EventType)
        for possible_type in all_types:
            if str(possible_type) == self.type:
                return possible_type.as_dict()

    @property
    def qr_code(self) -> Optional[str]:
        if not self.is_event_expired and not self.isCancelled:
            return generate_qr_code(booking_token=self.token,
                                    offer_extra_data=self.extraData)
        if not self.isUsed and not self.isCancelled:
            return generate_qr_code(booking_token=self.token,
                                    offer_extra_data=self.extraData)
        return None


class BeneficiaryBookings:
    def __init__(self, bookings: List[BeneficiaryBooking], stocks: List[Stock]):
        self.bookings = bookings
        self.stocks = stocks
