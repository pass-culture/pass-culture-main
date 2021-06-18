from pydantic import BaseModel
from pydantic.fields import Field

from pcapi.routes.adage.v1.serialization.prebooking import PreBookingResponse
from pcapi.serialization.utils import to_camel


class EducationalInstitutionResponse(BaseModel):
    UIACode: str = Field(description="Educational institution's UAI code")
    yearId: int = Field(description="Shared year id")
    name: str = Field(description="Educational institution name")
    creditTotal: int = Field(description="Total credit granted to the educational institution")
    creditUsed: int = Field(description="Credit consumed by already used bookings")
    creditBooked: int = Field(description="Credit booked by validated but not used bookings")
    prebookings: list[PreBookingResponse]

    class Config:
        title = "School response model"
        alias_generator = to_camel
        allow_population_by_field_name = True
