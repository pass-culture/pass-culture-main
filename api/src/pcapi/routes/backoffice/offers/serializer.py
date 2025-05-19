from pcapi.core.offers import models as offers_models
from pcapi.routes.backoffice.filters import format_date_time
from pcapi.routes.backoffice.filters import format_offer_status
from pcapi.routes.serialization import BaseModel


class OfferSerializer(BaseModel):
    id: int
    name: str
    venue_name: str
    venue_id: int
    status: str
    dateCreated: str

    @classmethod
    def from_orm(cls, offer: offers_models.Offer) -> "OfferSerializer":
        return cls(
            id=offer.id,
            name=offer.name,
            venue_name=offer.venue.common_name,
            venue_id=offer.venue.id,
            status=format_offer_status(offer.status),
            dateCreated=format_date_time(offer.dateCreated),
        )

    class Config:
        orm_mode = True
