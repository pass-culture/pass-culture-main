from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class EducationalInstitutionResponseModel(BaseModel):
    id: int
    name: str
    institutionType: str | None
    postalCode: str
    city: str
    phoneNumber: str

    class Config:
        orm_mode = True
        extra = "forbid"


class EducationalInstitutionsResponseModel(BaseModel):
    educational_institutions: list[EducationalInstitutionResponseModel]
    page: int
    pages: int
    total: int

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EducationalInstitutionsQueryModel(BaseModel):
    per_page_limit: int = 1000
    page: int = 1

    class Config:
        alias_generator = to_camel
        extra = "forbid"
