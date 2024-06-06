from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.serialization import BaseModel


class NationalProgramModel(BaseModel):
    id: int = fields.NATIONAL_PROGRAM_ID
    name: str = fields.NATIONAL_PROGRAM_NAME

    class Config:
        orm_mode = True


class ListNationalProgramsResponseModel(BaseModel):
    __root__: list[NationalProgramModel]
