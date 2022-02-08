from pcapi.routes.serialization import BaseModel


class VenueTypeResponseModel(BaseModel):
    id: str
    label: str


class VenueTypeListResponseModel(BaseModel):
    __root__: list[VenueTypeResponseModel]
