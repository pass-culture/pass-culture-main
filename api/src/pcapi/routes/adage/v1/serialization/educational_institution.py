from pydantic.v1.fields import Field

import pcapi.core.educational.schemas as educational_schemas
from pcapi.serialization.utils import to_camel


class EducationalInstitutionResponse(educational_schemas.AdageBaseResponseModel):
    credit: int = Field(description="Total credit granted to the educational institution")
    isFinal: bool = Field(description="Flag to know if the credit has been approved and is now final")
    prebookings: list[educational_schemas.EducationalBookingResponse]

    class Config:
        title = "School response model"
        alias_generator = to_camel
        allow_population_by_field_name = True
