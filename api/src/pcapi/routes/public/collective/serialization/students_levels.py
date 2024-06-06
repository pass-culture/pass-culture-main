from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.serialization import BaseModel


class CollectiveOffersStudentLevelResponseModel(BaseModel):
    id: str = fields.STUDENT_LEVEL_ID
    name: str = fields.STUDENT_LEVEL_NAME


class CollectiveOffersListStudentLevelsResponseModel(BaseModel):
    __root__: list[CollectiveOffersStudentLevelResponseModel]
