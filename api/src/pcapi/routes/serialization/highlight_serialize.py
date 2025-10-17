from datetime import datetime
from typing import Any

import pydantic.v1 as pydantic_v1

from pcapi.routes.serialization import ConfiguredBaseModel


class HighlightGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        highlight = self._obj
        if key == "availability_timespan":
            return highlight.availability_timespan.lower, highlight.availability_timespan.upper
        if key == "highlight_timespan":
            return highlight.highlight_timespan.lower, highlight.highlight_timespan.upper
        if key == "mediation_url":
            return highlight.mediation_url or ""
        return super().get(key, default)


class ShortHighlightResponseModel(ConfiguredBaseModel):
    id: int
    name: str


class HighlightResponseModel(ConfiguredBaseModel):
    id: int
    availability_timespan: tuple[datetime, datetime]
    description: str
    highlight_timespan: tuple[datetime, datetime]
    mediation_url: str
    name: str

    class Config:
        from_attributes = True
        getter_dict = HighlightGetterDict


class HighlightsResponseModel(ConfiguredBaseModel):
    __root__: list[HighlightResponseModel]
