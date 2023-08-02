from pcapi.routes.serialization import BaseModel


class NationalProgramModel(BaseModel):
    id: int
    name: str


class ListNationalProgramsResponseModel(BaseModel):
    __root__: list[NationalProgramModel]
