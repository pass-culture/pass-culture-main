from datetime import datetime

from pydantic.v1 import validator

import pcapi.core.offers.validation as offers_validation
from pcapi.routes.public.books_stocks import serialization
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class StocksResponseModel(BaseModel):
    stocks_count: int

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class StocksUpsertBodyModel(BaseModel):
    offer_id: int
    stocks: list[serialization.StockCreationBodyModel | serialization.StockEditionBodyModel]

    @validator("stocks")
    def check_max_stocks_per_offer_limit(
        cls, value: list[serialization.StockCreationBodyModel] | list[serialization.StockEditionBodyModel]
    ) -> list[serialization.StockCreationBodyModel] | list[serialization.StockEditionBodyModel]:
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
