import typing

import pydantic as pydantic_v2

from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.documentation_constants.fields_v2 import fields_v2
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


# National program models
class NationalProgramModelV2(HttpBodyModel):
    id: int = fields_v2.NATIONAL_PROGRAM_ID
    name: str = fields_v2.NATIONAL_PROGRAM_NAME


class ListNationalProgramsResponseModel(pydantic_v2.RootModel):
    root: list[NationalProgramModelV2]


class EducationalDomainResponseModel(HttpBodyModel):
    id: int
    name: str
    national_programs: list[NationalProgramModelV2]


# Domain models
class EducationalDomainsResponseModel(pydantic_v2.RootModel):
    root: list[EducationalDomainResponseModel]


class EducationalRedactorQueryModel(HttpQueryParamsModel):
    uai: typing.Annotated[str, pydantic_v2.Field(min_length=3)]
    candidate: typing.Annotated[str, pydantic_v2.Field(min_length=3)]


# Redactor models
class EducationalRedactor(HttpBodyModel):
    name: str
    surname: str
    gender: str | None = None
    email: str


class EducationalRedactors(pydantic_v2.RootModel):
    root: list[EducationalRedactor]


# Institution models
class EducationalInstitutionResponseModelV2(HttpBodyModel):
    id: int
    name: str
    institution_type: str | None = None
    postal_code: str
    city: str
    phone_number: str
    institution_id: str


class EducationalInstitutionsResponseModel(HttpBodyModel):
    educational_institutions: list[EducationalInstitutionResponseModelV2]
    page: int
    pages: int
    total: int


class EducationalInstitutionsQueryModel(HttpQueryParamsModel):
    per_page_limit: int = 1000
    page: int = 1


# Adage partners
class CulturalPartner(HttpBodyModel):
    id: int
    commune_libelle: str | None = None
    libelle: str
    region_libelle: str | None = None


class AdageCulturalPartnersResponseModel(HttpBodyModel):
    partners: list[CulturalPartner]


# Legacy (pydantic V1)
class NationalProgramModel(BaseModel):
    id: int = fields.NATIONAL_PROGRAM_ID
    name: str = fields.NATIONAL_PROGRAM_NAME


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
