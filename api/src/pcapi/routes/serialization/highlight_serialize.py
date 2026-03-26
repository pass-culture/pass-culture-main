import typing
from datetime import date
from datetime import timedelta

import psycopg2.extras
from pydantic import RootModel

from pcapi.core.highlights import models as highlights_models
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.serialization import HttpBodyModel


def get_inclusive_daterange_tuple_from_exclusive_daterange(daterange: psycopg2.extras.DateRange) -> tuple:
    return daterange.lower, daterange.upper - timedelta(days=1)


# TODO (tpommellet) migrate to HttpBodyModel when ListOffersOfferResponseModel is migrated
class ShortHighlightResponseModel(ConfiguredBaseModel):
    id: int
    name: str


class HighlightResponseModel(HttpBodyModel):
    id: int
    availability_datespan: list[date]
    description: str
    highlight_datespan: list[date]
    communication_date: date
    mediation_url: str
    name: str

    @classmethod
    def build(cls, highlight: highlights_models.Highlight) -> typing.Self:
        availability_start, availability_end = get_inclusive_daterange_tuple_from_exclusive_daterange(
            highlight.availability_datespan
        )
        highlight_start, highlight_end = get_inclusive_daterange_tuple_from_exclusive_daterange(
            highlight.highlight_datespan
        )
        return cls(
            id=highlight.id,
            availability_datespan=[availability_start, availability_end],
            description=highlight.description,
            highlight_datespan=[highlight_start, highlight_end],
            communication_date=highlight.communication_date,
            mediation_url=highlight.mediation_url,
            name=highlight.name,
        )


class HighlightsResponseModel(RootModel):
    root: list[HighlightResponseModel]
