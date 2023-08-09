from pcapi.routes.serialization import BaseModel


class NationalProgramModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ListNationalProgramsResponseModel(BaseModel):
    __root__: list[NationalProgramModel]
