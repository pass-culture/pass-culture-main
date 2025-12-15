from pydantic import RootModel

from pcapi.routes.serialization import HttpBodyModel


class VenueLabelResponseModel(HttpBodyModel):
    id: int
    label: str


class VenueLabelListResponseModel(RootModel):
    root: list[VenueLabelResponseModel]
