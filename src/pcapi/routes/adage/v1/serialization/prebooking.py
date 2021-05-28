from datetime import datetime
import enum
from typing import Optional

from pydantic import BaseModel

from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.native.v1.serialization.offers import OfferCategoryResponse
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.serialization.utils import to_camel


class PreBookingStatuses(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REFUSED = "REFUSED"
    USED = "USED"


class GetPreBookingsRequest(BaseModel):
    schoolId: str
    yearId: str
    redactorEmail: Optional[str]
    status: Optional[PreBookingStatuses]


class PreBookingResponse(BaseModel):
    address: str
    beginningDatetime: datetime
    cancellationDate: Optional[datetime]
    category: OfferCategoryResponse
    city: str
    confirmationDate: Optional[datetime]
    confirmationLimitDate: datetime
    coordinates: Coordinates
    expirationDate: Optional[datetime]
    id: int
    image: Optional[OfferImageResponse]
    isDigital: bool
    venueName: str
    name: str
    postalCode: str
    quantity: int
    redactorEmail: str
    schoolId: str
    status: PreBookingStatuses
    totalAmount: int
    url: Optional[str]
    withdrawalDetails: Optional[str]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class PreBookingsResponse(BaseModel):
    prebookings: list[PreBookingResponse]
