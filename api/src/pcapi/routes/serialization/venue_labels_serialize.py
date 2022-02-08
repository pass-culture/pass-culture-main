from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import humanize_field


class VenueLabelResponseModel(BaseModel):
    id: str
    label: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class VenueLabelListResponseModel(BaseModel):
    __root__: list[VenueLabelResponseModel]
