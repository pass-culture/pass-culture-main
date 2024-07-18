from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pydantic import ConfigDict


class EducationalInstitutionResponseModel(BaseModel):
    id: int
    name: str
    institutionType: str | None
    postalCode: str
    city: str
    phoneNumber: str
    institutionId: str
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class EducationalInstitutionsResponseModel(BaseModel):
    educational_institutions: list[EducationalInstitutionResponseModel]
    page: int
    pages: int
    total: int
    model_config = ConfigDict(alias_generator=to_camel, extra="forbid")


class EducationalInstitutionsQueryModel(BaseModel):
    per_page_limit: int = 1000
    page: int = 1
    model_config = ConfigDict(alias_generator=to_camel, extra="forbid")
