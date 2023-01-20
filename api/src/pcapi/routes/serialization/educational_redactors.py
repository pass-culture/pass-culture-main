from typing import TYPE_CHECKING

import pydantic

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class EducationalRedactorQueryModel(BaseModel):
    if TYPE_CHECKING:
        uai: str
        candidate: str
    else:
        uai: pydantic.constr(strip_whitespace=True, min_length=3)
        candidate: pydantic.constr(strip_whitespace=True, min_length=3)

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EducationalRedactor(BaseModel):
    name: str
    surname: str
    gender: str


class EducationalRedactors(BaseModel):
    __root__: list[EducationalRedactor]
