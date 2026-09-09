import typing

from pydantic import RootModel
from pydantic.types import StringConstraints

from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


Constraints = StringConstraints(min_length=3, strip_whitespace=True)


class EducationalRedactorQueryModel(HttpQueryParamsModel):
    uai: typing.Annotated[str, Constraints]
    candidate: typing.Annotated[str, Constraints]


class EducationalRedactor(HttpBodyModel):
    name: str
    surname: str
    email: str


class EducationalRedactors(RootModel):
    root: list[EducationalRedactor]
