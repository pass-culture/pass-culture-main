from pydantic.main import BaseModel


class ProviderResponse(BaseModel):
    id: str
    name: str
    localClass: str
    enabledForPro: bool
    isActive: bool


class ListProviderResponse(BaseModel):
    __root__: list[ProviderResponse]
