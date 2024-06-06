import typing

from pcapi.core.educational import models
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.national_programs import NationalProgramModel


class CollectiveOffersDomainResponseModel(BaseModel):
    id: int = fields.EDUCATIONAL_DOMAIN_ID
    name: str = fields.EDUCATIONAL_DOMAIN_NAME
    nationalPrograms: typing.Sequence[NationalProgramModel]

    class Config:
        orm_mode = True

    @classmethod
    def build(cls, domain: models.EducationalDomain) -> "CollectiveOffersDomainResponseModel":
        programs = [NationalProgramModel(id=program.id, name=program.name) for program in domain.nationalPrograms]
        return cls(id=domain.id, name=domain.name, nationalPrograms=programs)


class CollectiveOffersListDomainsResponseModel(BaseModel):
    __root__: list[CollectiveOffersDomainResponseModel]
