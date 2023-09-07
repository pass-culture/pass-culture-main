from pydantic.v1 import validator

from pcapi.core.educational.models import EducationalInstitution
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


MAX_LIMIT_EDUCATIONAL_INSTITUTION = 20


class CollectiveOffersEducationalInstitutionResponseModel(BaseModel):
    id: int
    uai: str
    name: str
    institutionType: str
    city: str
    postalCode: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, institution: EducationalInstitution) -> "CollectiveOffersEducationalInstitutionResponseModel":
        institution.uai = institution.institutionId
        return super().from_orm(institution)


class CollectiveOffersListEducationalInstitutionResponseModel(BaseModel):
    __root__: list[CollectiveOffersEducationalInstitutionResponseModel]


class GetListEducationalInstitutionsQueryModel(BaseModel):
    id: int | None
    name: str | None
    institution_type: str | None
    city: str | None
    postal_code: str | None
    uai: str | None
    limit: int = MAX_LIMIT_EDUCATIONAL_INSTITUTION

    @validator("limit")
    def validate_limit(cls, limit: int) -> int:
        limit = min(limit, MAX_LIMIT_EDUCATIONAL_INSTITUTION)
        return limit

    class Config:
        alias_generator = to_camel
        extra = "forbid"
