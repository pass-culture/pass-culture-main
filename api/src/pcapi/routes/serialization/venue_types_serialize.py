from pydantic import BaseModel

from pcapi.serialization.utils import humanize_field


class VenueTypeResponseModel(BaseModel):
    id: str
    label: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class VenueTypeListResponseModel(BaseModel):
    __root__: list[VenueTypeResponseModel]
