from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel


class NationalProgramResponseModel(HttpBodyModel):
    id: int
    name: str


# legacy pydantic v1 models
class NationalProgramModel(BaseModel):
    id: int = fields.NATIONAL_PROGRAM_ID
    name: str = fields.NATIONAL_PROGRAM_NAME

    class Config:
        orm_mode = True


class ListNationalProgramsResponseModel(BaseModel):
    __root__: list[NationalProgramModel]
