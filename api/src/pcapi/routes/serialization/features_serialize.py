from pydantic import ConfigDict
from pydantic import RootModel

from pcapi.routes.serialization import BaseModelV2


class FeatureResponseModel(BaseModelV2):
    description: str
    id: int
    isActive: bool
    name: str
    nameKey: str

    model_config = ConfigDict(from_attributes=True)


class ListFeatureResponseModel(RootModel, BaseModelV2):
    root: list[FeatureResponseModel]
