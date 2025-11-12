from pydantic import ConfigDict
from pydantic import RootModel

from pcapi.routes.serialization import HttpBodyModel


class FeatureResponseModel(HttpBodyModel):
    description: str
    id: int
    isActive: bool
    name: str
    nameKey: str

    model_config = ConfigDict(from_attributes=True)


class ListFeatureResponseModel(RootModel, HttpBodyModel):
    root: list[FeatureResponseModel]
