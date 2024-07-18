from pydantic.v1.main import BaseModel
from pydantic import ConfigDict


class ProviderResponse(BaseModel):
    id: int
    name: str
    enabledForPro: bool
    isActive: bool
    hasOffererProvider: bool
    model_config = ConfigDict(from_attributes=True)


class ListProviderResponse(BaseModel):
    __root__: list[ProviderResponse]
