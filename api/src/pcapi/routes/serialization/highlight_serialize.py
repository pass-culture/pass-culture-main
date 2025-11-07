from datetime import date
from datetime import timedelta
from typing import Any

import psycopg2.extras
import pydantic.v1 as pydantic_v1

from pcapi.routes.serialization import ConfiguredBaseModel


def get_inclusive_daterange_tuple_from_exclusive_daterange(daterange: psycopg2.extras.DateRange) -> tuple:
    return daterange.lower, daterange.upper - timedelta(days=1)


class HighlightGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        highlight = self._obj
        if key == "availability_datespan":
            return get_inclusive_daterange_tuple_from_exclusive_daterange(highlight.availability_datespan)
        if key == "highlight_datespan":
            return get_inclusive_daterange_tuple_from_exclusive_daterange(highlight.highlight_datespan)
        if key == "mediation_url":
            return highlight.mediation_url or ""
        return super().get(key, default)


class ShortHighlightResponseModel(ConfiguredBaseModel):
    id: int
    name: str


class HighlightResponseModel(ConfiguredBaseModel):
    id: int
    availability_datespan: list[date]
    description: str
    highlight_datespan: list[date]
    communication_date: date
    mediation_url: str
    name: str

    class Config:
        from_attributes = True
        getter_dict = HighlightGetterDict


class HighlightsResponseModel(ConfiguredBaseModel):
    __root__: list[HighlightResponseModel]
