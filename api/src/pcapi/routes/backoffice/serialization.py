import typing

import pydantic

from pcapi.routes.serialization import BaseModel


class Permission(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    category: typing.Optional[str]


class Role(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    permissions: list[Permission]


class ListRoleResponseModel(BaseModel):
    class Config:
        orm_mode = True

    roles: list[Role]


class ListPermissionResponseModel(BaseModel):
    class Config:
        orm_mode = True

    permissions: list[Permission]


class NewRoleRequestModel(BaseModel):
    name: str = pydantic.Field(..., min_length=1)
    permissionIds: list[int]
