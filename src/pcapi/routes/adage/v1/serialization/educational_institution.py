from datetime import datetime

from pydantic import BaseModel
from pydantic.fields import Field

from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class EducationalInstitutionResponse(BaseModel):
    credit: int = Field(description="Total credit granted to the educational institution")
    isFinal: bool = Field(description="Flag to know if the credit has been approved and is now final")
    prebookings: list[EducationalBookingResponse]

    class Config:
        title = "School response model"
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
