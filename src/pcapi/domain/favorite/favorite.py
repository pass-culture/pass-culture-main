from pcapi.core.offers.models import Mediation
from pcapi.models import Offer


class FavoriteDomain:
    def __init__(self, identifier: int, mediation: Mediation, offer: Offer, booking: dict):
        self.identifier = identifier
        self.mediation = mediation
        self.offer = offer
        self.booking_identifier = booking["id"] if booking else None
        self.booked_stock_identifier = booking["stock_id"] if booking else None
        self.booking_quantity = booking["quantity"] if booking else None

    @property
    def is_booked(self) -> bool:
        return bool(self.booking_identifier)

    @property
    def thumb_url(self) -> str:
        if self.mediation:
            return self.mediation.thumbUrl
        return self.offer.thumbUrl
