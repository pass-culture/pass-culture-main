import typing

from pcapi.routes.serialization import BaseModel


class Permission(BaseModel):
    class Config:
        orm_mode = True

    name: str
    category: typing.Optional[str]


class Role(BaseModel):
    class Config:
        orm_mode = True

    name: str
    permissions: list[Permission]


class ListRoleResponseModel(BaseModel):
    class Config:
        orm_mode = True

    roles: list[Role]
