import typing

import pydantic as pydantic_v2

from pcapi.routes.serialization import HttpBodyModel


class ResetPasswordBodyModel(HttpBodyModel):
    email: pydantic_v2.EmailStr
    token: typing.Annotated[str, pydantic_v2.Field(min_length=1)]


class NewPasswordBodyModel(HttpBodyModel):
    token: typing.Annotated[str, pydantic_v2.Field(min_length=1)]
    newPassword: typing.Annotated[str, pydantic_v2.Field(min_length=1)]


class CheckTokenBodyModel(HttpBodyModel):
    token: typing.Annotated[str, pydantic_v2.Field(min_length=1)]
