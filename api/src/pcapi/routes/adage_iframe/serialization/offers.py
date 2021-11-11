from datetime import datetime
import logging
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from pcapi.core.offers.models import Offer
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class OfferStockResponse(BaseModel):
    id: int
    beginningDatetime: Optional[datetime]
    isBookable: bool
    price: int

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class OfferVenueResponse(BaseModel):
    @classmethod
    def from_orm(cls, venue):  # type: ignore
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        result = super().from_orm(venue)
        return result

    id: int
    address: Optional[str]
    city: Optional[str]
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]
    coordinates: Coordinates

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class OfferResponse(BaseModel):
    @classmethod
    def from_orm(cls: Any, offer: Offer):  # type: ignore
        offer.subcategoryLabel = offer.subcategory.app_label
        offer.isExpired = offer.hasBookingLimitDatetimesPassed

        result = super().from_orm(offer)

        return result

    id: int
    subcategoryLabel: str
    description: Optional[str]
    isExpired: bool
    isSoldOut: bool
    name: str
    stocks: list[OfferStockResponse]
    venue: OfferVenueResponse

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
