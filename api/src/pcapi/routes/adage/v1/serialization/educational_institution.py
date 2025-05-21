from pydantic.v1.fields import Field

from pcapi.serialization.educational.adage import shared as adage_serialize
from pcapi.serialization.utils import to_camel


class EducationalInstitutionResponse(adage_serialize.AdageBaseResponseModel):
    credit: int = Field(description="Total credit granted to the educational institution")
    isFinal: bool = Field(description="Flag to know if the credit has been approved and is now final")
    prebookings: list[adage_serialize.EducationalBookingResponse]

    class Config:
        title = "School response model"
        alias_generator = to_camel
        allow_population_by_field_name = True
