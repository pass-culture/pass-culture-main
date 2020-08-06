from typing import Dict

from models import OfferSQLEntity, MediationSQLEntity


class Favorite(object):
    def __init__(self, identifier: int, mediation: MediationSQLEntity, offer: OfferSQLEntity, booking: Dict):
        self.identifier = identifier
        self.mediation = mediation
        self.offer = offer
        self.booking_identifier = booking['id'] if booking else None
        self.booked_stock_identifier = booking['stock_id'] if booking else None

    @property
    def is_booked(self) -> bool:
        return True if self.booking_identifier else False

    @property
    def thumb_url(self) -> str:
        if self.mediation:
            return self.mediation.thumbUrl
        return self.offer.thumb_url
