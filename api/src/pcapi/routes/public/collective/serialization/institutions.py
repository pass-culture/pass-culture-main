from pydantic.v1 import Field
from pydantic.v1 import validator

from pcapi.core.educational.models import EducationalInstitution
from pcapi.routes.public.documentation_constants.fields import LIMIT_DESCRIPTION
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


MAX_LIMIT_EDUCATIONAL_INSTITUTION = 20


class CollectiveOffersEducationalInstitutionResponseModel(BaseModel):
    id: int = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_ID
    uai: str = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_UAI
    name: str = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_NAME
    institutionType: str = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_TYPE
    city: str = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_CITY
    postalCode: str = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_POSTAL_CODE

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, institution: EducationalInstitution) -> "CollectiveOffersEducationalInstitutionResponseModel":
        institution.uai = institution.institutionId
        return super().from_orm(institution)


class CollectiveOffersListEducationalInstitutionResponseModel(BaseModel):
    __root__: list[CollectiveOffersEducationalInstitutionResponseModel]


class GetListEducationalInstitutionsQueryModel(BaseModel):
    id: int | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_ID
    name: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_NAME
    institution_type: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_TYPE
    city: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_CITY
    postal_code: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_POSTAL_CODE
    uai: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_UAI
    limit: int = Field(MAX_LIMIT_EDUCATIONAL_INSTITUTION, description=LIMIT_DESCRIPTION, example=10)

    @validator("limit")
    def validate_limit(cls, limit: int) -> int:
        limit = min(limit, MAX_LIMIT_EDUCATIONAL_INSTITUTION)
        return limit

    class Config:
        alias_generator = to_camel
        extra = "forbid"
