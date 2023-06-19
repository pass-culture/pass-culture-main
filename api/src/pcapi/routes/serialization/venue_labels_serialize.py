from pcapi.routes.serialization import BaseModel


class VenueLabelResponseModel(BaseModel):
    id: int
    label: str

    class Config:
        orm_mode = True


class VenueLabelListResponseModel(BaseModel):
    __root__: list[VenueLabelResponseModel]
