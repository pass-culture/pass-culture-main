from datetime import datetime
import enum
from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field

from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.native.v1.serialization.offers import OfferCategoryResponse
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.serialization.utils import to_camel


class PreBookingStatuses(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REFUSED = "REFUSED"
    USED = "USED"
    USED_BY_INSTITUTE = "USED_BY_INSTITUTE"
    CANCELLED = "CANCELLED"


class GetPreBookingsRequest(BaseModel):
    redactorEmail: Optional[str] = Field(description="Email of querying redactor")
    status: Optional[PreBookingStatuses] = Field(description="Status of retrieved preboookings")

    class Config:
        title = "Prebookings query filters"


class Redactor(BaseModel):
    email: str
    redactorFirstName: str
    redactorLastName: str
    redactorCivility: str

    class Config:
        alias_generator = to_camel


class PreBookingResponse(BaseModel):
    address: str = Field(description="Adresse of event")
    beginningDatetime: datetime = Field(description="Beginnning date of event")
    cancellationDate: Optional[datetime] = Field(description="Date of cancellation if prebooking is cancelled")
    cancellationLimitDate: Optional[datetime] = Field(description="Limit date to cancel the prebooking")
    category: OfferCategoryResponse = Field(description="pass Culture's category of cultural offer")
    city: str
    confirmationDate: Optional[datetime] = Field(description="Date of confirmation if prebooking is confirmed")
    confirmationLimitDate: datetime = Field(description="Limit date to confirm the prebooking")
    coordinates: Coordinates = Field(description="Accurate coordinates of event")
    expirationDate: Optional[datetime] = Field(description="Expiration date after which booking is cancelled")
    id: int = Field(description="pass Culture's prebooking id")
    image: Optional[OfferImageResponse] = Field(description="passculture.app's image of cultural offer")
    isDigital: bool = Field(description="If true the event is accessed digitally")
    venueName: str = Field(description="Name of cultural venue proposing the event")
    name: str = Field(description="Name of event")
    postalCode: str
    quantity: int = Field(description="Number of place prebooked")
    redactor: Redactor
    UAICode: str = Field(description="Educational institution UAI code")
    yearId: int = Field(description="Shared year id")
    status: PreBookingStatuses
    totalAmount: int = Field(description="Total price of the prebooking")
    url: Optional[str] = Field(description="Url to access the offer")
    withdrawalDetails: Optional[str]

    class Config:
        title = "Prebooking detailed response"
        alias_generator = to_camel
        allow_population_by_field_name = True


class PreBookingsResponse(BaseModel):
    prebookings: list[PreBookingResponse]

    class Config:
        title = "List of prebookings"
