from typing import TYPE_CHECKING

import pydantic.v1 as pydantic_v1

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class EducationalRedactorQueryModel(BaseModel):
    if TYPE_CHECKING:
        uai: str
        candidate: str
    else:
        uai: pydantic_v1.constr(strip_whitespace=True, min_length=3)
        candidate: pydantic_v1.constr(strip_whitespace=True, min_length=3)

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EducationalRedactor(BaseModel):
    name: str
    surname: str
    gender: str | None
    email: str


class EducationalRedactors(BaseModel):
    __root__: list[EducationalRedactor]
