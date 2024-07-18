from pcapi.routes.serialization import BaseModel
from pydantic import ConfigDict


class EducationalDomainResponseModel(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class EducationalDomainsResponseModel(BaseModel):
    __root__: list[EducationalDomainResponseModel]
    model_config = ConfigDict(from_attributes=True)
