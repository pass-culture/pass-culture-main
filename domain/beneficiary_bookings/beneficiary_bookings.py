from datetime import datetime
from typing import List, Optional, Dict

from domain.beneficiary_bookings.stock import Stock
from models.offer_type import ProductType, ThingType, EventType
from utils.human_ids import humanize


def compute_offer_is_fully_booked(stocks: List[Stock]) -> bool:
    bookable_stocks = [stock for stock in stocks if stock.is_bookable]
    has_unlimited_stock = any(map(lambda stock: stock.quantity is None, stocks))
    if has_unlimited_stock:
        return False

    total_remaining_quantity = sum(
        [stock.remainingQuantity for stock in bookable_stocks if stock.remainingQuantity is not None])
    return total_remaining_quantity <= 0


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
                 description: str,
                 durationMinutes: int,
                 extraData: Dict,
                 isDuo: bool,
                 withdrawalDetails: str,
                 mediaUrls: List[str],
                 isNational: bool,
                 venueName: str,
                 address: str,
                 postalCode: str,
                 city: str,
                 latitude: float,
                 longitude: float,
                 price: float,
                 stocks: List[Stock]
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
        self.offerIsFullyBooked = compute_offer_is_fully_booked(stocks)

    @property
    def booking_access_url(self) -> str:
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
    def is_fully_booked(self):
        return self.offerIsFullyBooked


class BeneficiaryBookings:
    def __init__(self, bookings: List[BeneficiaryBooking], stocks: List[Stock]):
        self.bookings = bookings
        self.stocks = stocks
