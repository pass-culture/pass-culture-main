import datetime
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


class RoleRequestModel(BaseModel):
    name: str = pydantic.Field(..., min_length=1)
    permissionIds: list[int]


class PublicAccount(BaseModel):
    class Config:
        orm_mode = True

    id: int
    firstName: typing.Optional[str]
    lastName: typing.Optional[str]
    dateOfBirth: typing.Optional[datetime.datetime]
    email: str
    phoneNumber: typing.Optional[str]


class PublicAccountSearchQuery(BaseModel):
    q: str


class ListPublicAccountsResponseModel(BaseModel):
    class Config:
        orm_mode = True

    accounts: list[PublicAccount]


class GetBeneficiaryCreditResponseModel(BaseModel):
    initialCredit: float
    remainingCredit: float
    remainingDigitalCredit: float
