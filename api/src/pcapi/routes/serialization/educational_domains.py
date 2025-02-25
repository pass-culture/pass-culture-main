from pcapi.core.educational import models as educational_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import national_programs


class EducationalDomainResponseModel(BaseModel):
    id: int
    name: str
    nationalPrograms: list[national_programs.NationalProgramModel]

    @classmethod
    def from_orm(cls, domain: educational_models.EducationalDomain) -> "EducationalDomainResponseModel":
        result = super().from_orm(domain)
        result.nationalPrograms = [
            national_programs.NationalProgramModel.from_orm(program)
            for program in domain.nationalPrograms
            if program.isActive
        ]

        return result

    class Config:
        orm_mode = True


class EducationalDomainsResponseModel(BaseModel):
    __root__: list[EducationalDomainResponseModel]

    class Config:
        orm_mode = True
