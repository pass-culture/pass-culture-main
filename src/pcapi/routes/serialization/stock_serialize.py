from typing import Optional

from pydantic import BaseModel
from pcapi.serialization.utils import (
    to_camel,
    dehumanize_field,
    humanize_field,
)


class StockCreationBodyModel(BaseModel):
    beginning_datetime: Optional[str]
    booking_limit_datetime: Optional[str]
    offer_id: int
    price: float
    quantity: Optional[int]
    has_been_migrated: Optional[bool]

    # FIXME (cgaunet, 2020-11-05): these two fields are actually
    # unused for the stock creation
    beginning_time: Optional[str]
    offerer_id: Optional[str]

    _dehumanize_offer_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class StockEditionBodyModel(BaseModel):
    beginning_datetime: Optional[str]
    booking_limit_datetime: Optional[str]
    offer_id: Optional[int]
    price: Optional[float]
    quantity: Optional[int]
    has_been_migrated: Optional[bool]

    # FIXME (cgaunet, 2020-11-05): these two fields are actually
    # unused for the stock creation
    beginning_time: Optional[str]
    offerer_id: Optional[str]

    _dehumanize_offer_id = dehumanize_field("offer_id")

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
