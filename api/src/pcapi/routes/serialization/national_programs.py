from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.serialization import BaseModel
from pydantic import ConfigDict


class NationalProgramModel(BaseModel):
    id: int = fields.NATIONAL_PROGRAM_ID
    name: str = fields.NATIONAL_PROGRAM_NAME
    model_config = ConfigDict(from_attributes=True)


class ListNationalProgramsResponseModel(BaseModel):
    __root__: list[NationalProgramModel]
