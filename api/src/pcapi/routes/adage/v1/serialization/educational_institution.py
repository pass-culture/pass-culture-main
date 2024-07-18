from pydantic.v1.fields import Field

from pcapi.routes.adage.v1.serialization.config import AdageBaseResponseModel
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.serialization.utils import to_camel
from pydantic import ConfigDict


class EducationalInstitutionResponse(AdageBaseResponseModel):
    credit: int = Field(description="Total credit granted to the educational institution")
    isFinal: bool = Field(description="Flag to know if the credit has been approved and is now final")
    prebookings: list[EducationalBookingResponse]
    model_config = ConfigDict(title="School response model", alias_generator=to_camel, populate_by_name=True)
