from pcapi.routes.serialization import BaseModel
from pydantic import ConfigDict


class FeatureResponseModel(BaseModel):
    description: str
    id: str
    isActive: bool
    name: str
    nameKey: str
    model_config = ConfigDict(from_attributes=True)


class ListFeatureResponseModel(BaseModel):
    __root__: list[FeatureResponseModel]
