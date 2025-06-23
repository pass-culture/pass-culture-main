import typing

from pcapi.routes.serialization import BaseModel


class FeatureResponseModel(BaseModel):
    description: str
    id: str
    isActive: bool
    name: str
    nameKey: str

    class Config:
        orm_mode = True


class ListFeatureResponseModel(BaseModel):
    features: typing.Sequence[FeatureResponseModel]
