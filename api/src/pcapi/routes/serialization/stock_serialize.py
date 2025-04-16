from datetime import datetime
import decimal

from pydantic.v1 import Field
from pydantic.v1 import validator

from pcapi.core.offers import models
import pcapi.core.offers.validation as offers_validation
from pcapi.routes.serialization import BaseModel
import pcapi.serialization.utils as serialization_utils
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


######################


class ThingStockCreateBodyModel(BaseModel):
    offer_id: int
    price: decimal.Decimal

    activation_codes: list[str] | None
    activation_codes_expiration_datetime: datetime | None
    booking_limit_datetime: datetime | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)

    class Config:
        alias_generator = to_camel
        json_encoders = {datetime: format_into_utc_date}
        extra = "forbid"


class ThingStockUpdateBodyModel(BaseModel):
    price: decimal.Decimal
    booking_limit_datetime: datetime | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)

    class Config:
        alias_generator = to_camel
        json_encoders = {datetime: format_into_utc_date}
        extra = "forbid"


class StockCreationBodyModel(BaseModel):
    activation_codes: list[str] | None
    activation_codes_expiration_datetime: datetime | None
    beginning_datetime: datetime | None
    booking_limit_datetime: datetime | None
    price: decimal.Decimal | None
    price_category_id: int | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")
    _validate_activation_codes_expiration_datetime = serialization_utils.validate_datetime(
        "activation_codes_expiration_datetime"
    )

    class Config:
        alias_generator = to_camel
        json_encoders = {datetime: format_into_utc_date}
        extra = "forbid"


class StockEditionBodyModel(BaseModel):
    beginning_datetime: datetime | None
    booking_limit_datetime: datetime | None
    id: int
    price: decimal.Decimal | None
    price_category_id: int | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


######################


class StocksResponseModel(BaseModel):
    stocks_count: int

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class StocksUpsertBodyModel(BaseModel):
    offer_id: int
    stocks: list[StockCreationBodyModel | StockEditionBodyModel]

    @validator("stocks")
    def check_max_stocks_per_offer_limit(
        cls, value: list[StockCreationBodyModel] | list[StockEditionBodyModel]
    ) -> list[StockCreationBodyModel] | list[StockEditionBodyModel]:
        offers_validation.check_stocks_quantity(len(value))
        return value

    class Config:
        alias_generator = to_camel


class StockIdResponseModel(BaseModel):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
