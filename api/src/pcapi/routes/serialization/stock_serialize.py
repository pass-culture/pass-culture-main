import decimal
import typing

import pydantic as pydantic_v2
from typing_extensions import Annotated

import pcapi.serialization.utils as serialization_utils
from pcapi.core.offers import models
from pcapi.routes.serialization import HttpBodyModel


Quantity = Annotated[int, pydantic_v2.Field(ge=0, le=models.Stock.MAX_STOCK_QUANTITY)]

# convert to string before building a `decimal.Decimal` object because
# doing so with a float will lead to an unexpected value.
# eg. value = 19.95 ; Decimal(value) -> Decimal('19.9409718987...')
# Decimal(str(value)) -> Decimal('19.95')
Decimal = Annotated[decimal.Decimal, lambda value: decimal.Decimal(str(value))]


class ThingStockUpsertBodyModel(HttpBodyModel):
    id: int | None = None
    activation_codes: list[str] | None = None
    activation_codes_expiration_datetime: serialization_utils.future_tz_aware_datetime | None = None
    booking_limit_datetime: serialization_utils.future_tz_aware_datetime | None = None
    offer_id: int
    price: Decimal
    quantity: int | None = None


class ThingStocksBulkUpsertBodyModel(HttpBodyModel):
    stocks: list[ThingStockUpsertBodyModel]


class EventStockCreateBodyModel(HttpBodyModel):
    beginning_datetime: serialization_utils.future_tz_aware_datetime
    price_category_id: int
    quantity: Quantity | None = None
    booking_limit_datetime: serialization_utils.future_tz_aware_datetime | None = None


class EventStockUpdateBodyModel(EventStockCreateBodyModel):
    id: int


class EventStocksBulkCreateBodyModel(HttpBodyModel):
    offer_id: int
    stocks: list[EventStockCreateBodyModel]


class EventStocksBulkUpdateBodyModel(HttpBodyModel):
    offer_id: int
    stocks: list[EventStockUpdateBodyModel]


EventStocksList = typing.TypeVar("EventStocksList", list[EventStockCreateBodyModel], list[EventStockUpdateBodyModel])
