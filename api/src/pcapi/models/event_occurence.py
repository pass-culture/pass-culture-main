import datetime
import decimal

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory


class EventOccurrence:
    def __init__(
        self,
        offer: Offer,
        price: decimal.Decimal,
        price_category: PriceCategory,
        beginning_datetime: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=2),
    ) -> None:
        self.offer = offer
        self.offerId = offer.id
        self.beginningDatetime = beginning_datetime
        self.price = price
        self.price_category = price_category

    offer: Offer
    offerId: int
    beginningDatetime: datetime.datetime
    price: decimal.Decimal
    price_category: PriceCategory
