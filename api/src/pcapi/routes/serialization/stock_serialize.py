from datetime import datetime
import decimal
import typing

from pydantic.v1 import Field

from pcapi.core.offers import models
from pcapi.routes.serialization import BaseModel
import pcapi.serialization.utils as serialization_utils
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class ThingStockCreateBodyModel(BaseModel):
    offer_id: int
    price: decimal.Decimal

    activation_codes: list[str] | None
    activation_codes_expiration_datetime: datetime | None
    booking_limit_datetime: datetime | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)

    _validate_activation_codes_expiration_datetime = serialization_utils.validate_datetime(
        "activation_codes_expiration_datetime"
    )
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class ThingStockUpdateBodyModel(BaseModel):
    price: decimal.Decimal
    booking_limit_datetime: datetime | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)

    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EventStockCreateBodyModel(BaseModel):
    beginning_datetime: datetime
    price_category_id: int
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)
    booking_limit_datetime: datetime | None

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EventStockUpdateBodyModel(EventStockCreateBodyModel):
    id: int

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class StocksResponseModel(BaseModel):
    stocks_count: int

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class EventStocksBulkCreateBodyModel(BaseModel):
    offer_id: int
    stocks: list[EventStockCreateBodyModel]

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EventStocksBulkUpdateBodyModel(BaseModel):
    offer_id: int
    stocks: list[EventStockUpdateBodyModel]

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class StockIdResponseModel(BaseModel):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


EventStocksList = typing.TypeVar("EventStocksList", list[EventStockCreateBodyModel], list[EventStockUpdateBodyModel])
