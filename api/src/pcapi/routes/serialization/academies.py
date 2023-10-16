from pcapi.core.educational import academies
from pcapi.routes.serialization import BaseModel


class AcademiesResponseModel(BaseModel):
    __root__: list[str]

    @classmethod
    def build(cls) -> "AcademiesResponseModel":
        return cls(__root__=list(academies.ACADEMIES))
