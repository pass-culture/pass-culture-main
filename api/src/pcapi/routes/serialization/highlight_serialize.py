from datetime import datetime

from pcapi.routes.serialization import ConfiguredBaseModel


class HighlightResponseModel(ConfiguredBaseModel):
    availability_timespan: tuple[datetime, datetime]
    description: str
    highlight_timespan: tuple[datetime, datetime]
    mediation_url: str
    name: str

    class Config:
        from_attributes = True


class HighlightsResponseModel(ConfiguredBaseModel):
    __root__: list[HighlightResponseModel]
