import typing
from datetime import datetime

import pydantic as pydantic_v2
from typing_extensions import Annotated

import pcapi.serialization.utils as serialization_utils
from pcapi.core.offers import models
from pcapi.routes.serialization import HttpBodyModel


Quantity = Annotated[int, pydantic_v2.Field(ge=0, le=models.Stock.MAX_STOCK_QUANTITY)]


class ThingStockUpsertBodyModel(HttpBodyModel):
    id: int | None = None
    activation_codes: list[str] | None = None
    activation_codes_expiration_datetime: datetime | None = None
    booking_limit_datetime: datetime | None = None
    offer_id: int
    price: float
    quantity: int | None = None

    @pydantic_v2.field_validator("booking_limit_datetime", "activation_codes_expiration_datetime", mode="after")
    @classmethod
    def validate_datetime(cls, value: datetime | None) -> datetime | None:
        return serialization_utils.check_date_in_future_and_remove_timezone(value, pydantic_version="v2")


class ThingStocksBulkUpsertBodyModel(HttpBodyModel):
    stocks: list[ThingStockUpsertBodyModel]


class EventStockCreateBodyModel(HttpBodyModel):
    beginning_datetime: datetime
    price_category_id: int
    quantity: Quantity | None = None
    booking_limit_datetime: datetime | None = None

    @pydantic_v2.field_validator("beginning_datetime", "booking_limit_datetime", mode="after")
    @classmethod
    def validate_datetime(cls, value: datetime | None) -> datetime | None:
        return serialization_utils.check_date_in_future_and_remove_timezone(value, pydantic_version="v2")


class EventStockUpdateBodyModel(EventStockCreateBodyModel):
    id: int


class EventStocksBulkCreateBodyModel(HttpBodyModel):
    offer_id: int
    stocks: list[EventStockCreateBodyModel]


class EventStocksBulkUpdateBodyModel(HttpBodyModel):
    offer_id: int
    stocks: list[EventStockUpdateBodyModel]


EventStocksList = typing.TypeVar("EventStocksList", list[EventStockCreateBodyModel], list[EventStockUpdateBodyModel])
