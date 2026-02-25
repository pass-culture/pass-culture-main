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
    per_page_limit: int = 1000
    page: int = 1
