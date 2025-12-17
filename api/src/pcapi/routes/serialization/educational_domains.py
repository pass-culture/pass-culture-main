import typing

from pydantic import RootModel

from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import national_programs


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import EducationalDomain


class EducationalDomainResponseModel(HttpBodyModel):
    id: int
    name: str
    nationalPrograms: list[national_programs.NationalProgramResponseModel]

    @classmethod
    def build(cls, domain: "EducationalDomain") -> "EducationalDomainResponseModel":
        return cls(
            id=domain.id,
            name=domain.name,
            nationalPrograms=[
                national_programs.NationalProgramResponseModel.model_validate(program)
                for program in domain.nationalPrograms
                if program.isActive
            ],
        )


class EducationalDomainsResponseModel(RootModel):
    root: list[EducationalDomainResponseModel]
