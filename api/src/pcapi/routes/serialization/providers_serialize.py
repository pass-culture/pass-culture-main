from pydantic.main import BaseModel

from pcapi.serialization.utils import humanize_field


class ProviderResponse(BaseModel):
    id: str
    name: str
    enabledForPro: bool
    isActive: bool

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class ListProviderResponse(BaseModel):
    __root__: list[ProviderResponse]
