from pcapi.routes.serialization import BaseModel


class CollectiveOffersStudentLevelResponseModel(BaseModel):
    id: str
    name: str


class CollectiveOffersListStudentLevelsResponseModel(BaseModel):
    __root__: list[CollectiveOffersStudentLevelResponseModel]
