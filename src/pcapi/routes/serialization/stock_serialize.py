import datetime
from typing import Any
from typing import Optional

from pydantic import BaseModel

from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel


class StockCreationBodyModel(BaseModel):
    beginning_datetime: Optional[datetime.datetime]
    booking_limit_datetime: Optional[datetime.datetime]
    offer_id: int
    price: float
    quantity: Optional[int]

    # FIXME (cgaunet, 2020-11-05): these two fields are actually
    # unused for the stock creation. But the webapp does send them so
    # we must list them here (because of the `extra = "forbid"` below.
    beginning_time: Optional[str]
    offerer_id: Optional[str]

    _dehumanize_offer_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class StockEditionBodyModel(BaseModel):
    beginning_datetime: Optional[datetime.datetime]
    booking_limit_datetime: Optional[datetime.datetime]
    offer_id: Optional[str]
    price: Optional[float]
    quantity: Optional[int]

    # FIXME (cgaunet, 2020-11-05): these three fields are actually
    # unused for the stock edition. But the webapp does send them so
    # we must list them here (because of the `extra = "forbid"` below.
    beginning_time: Optional[str]
    offerer_id: Optional[str]
    id: Optional[Any]

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class StockResponseIdModel(BaseModel):
    id: str

    _humanize_offer_id = humanize_field("id")

    class Config:  # pylint: disable=too-few-public-methods
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
