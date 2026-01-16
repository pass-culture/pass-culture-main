from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


# this v1 model is still used in collective offer serialize
class EducationalInstitutionResponseModel(BaseModel):
    id: int
    name: str
    institutionType: str | None
    postalCode: str
    city: str
    phoneNumber: str
    institutionId: str

    class Config:
        orm_mode = True
        extra = "forbid"


class EducationalInstitutionResponseModelV2(HttpBodyModel):
    id: int
    name: str
    institutionType: str | None
    postalCode: str
    city: str
    phoneNumber: str
    institutionId: str


class EducationalInstitutionsResponseModel(HttpBodyModel):
    educational_institutions: list[EducationalInstitutionResponseModelV2]
    page: int
    pages: int
    total: int


class EducationalInstitutionsQueryModel(HttpQueryParamsModel):
    per_page_limit: int = 1000
    page: int = 1
