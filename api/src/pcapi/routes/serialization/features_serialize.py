from pydantic import RootModel

from pcapi.routes.serialization import HttpBodyModel


class FeatureResponseModel(HttpBodyModel):
    id: int
    name: str
    is_active: bool


class ListFeatureResponseModel(RootModel):
    root: list[FeatureResponseModel]
