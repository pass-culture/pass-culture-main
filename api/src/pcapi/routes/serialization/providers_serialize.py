from pydantic.main import BaseModel


class ProviderResponse(BaseModel):
    id: int
    name: str
    enabledForPro: bool
    isActive: bool

    class Config:
        orm_mode = True


class ListProviderResponse(BaseModel):
    __root__: list[ProviderResponse]
