import pydantic as pydantic_v2

from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class EducationalInstitutionResponseModel(HttpBodyModel):
    id: int
    name: str
    institutionType: str
    postalCode: str
    city: str
    phoneNumber: str
    institutionId: str


class EducationalInstitutionsResponseModel(HttpBodyModel):
    educational_institutions: list[EducationalInstitutionResponseModel]
    page: int
    pages: int
    total: int


class EducationalInstitutionsQueryModel(HttpQueryParamsModel):
    per_page_limit: int = pydantic_v2.Field(default=1000, ge=1, le=1000)
    page: int = pydantic_v2.Field(default=1, ge=1)
