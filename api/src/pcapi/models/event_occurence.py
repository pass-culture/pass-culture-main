from datetime import datetime
from datetime import timedelta

from pcapi.core.offers.models import Offer


class EventOccurrence:
    def __init__(self, offer: Offer, beginning_datetime: datetime = datetime.utcnow() + timedelta(hours=2)) -> None:
        self.offer = offer
        self.offerId = offer.id
        self.beginningDatetime = beginning_datetime

    offer: Offer
    offerId: int
    beginningDatetime: datetime
