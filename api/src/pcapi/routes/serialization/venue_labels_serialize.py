from pcapi.routes.serialization import BaseModel
from pydantic import ConfigDict


class VenueLabelResponseModel(BaseModel):
    id: int
    label: str
    model_config = ConfigDict(from_attributes=True)


class VenueLabelListResponseModel(BaseModel):
    __root__: list[VenueLabelResponseModel]
