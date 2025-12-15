from pydantic import RootModel

from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel


class VenueTypeResponseModelV2(HttpBodyModel):
    value: str
    label: str


class VenueTypeListResponseModel(RootModel):
    root: list[VenueTypeResponseModelV2]


# Legacy (pydantic V1)
class VenueTypeResponseModel(BaseModel):
    value: str
    label: str
