from datetime import datetime
import decimal
import logging
import typing

import pydantic.v1 as pydantic_v1
from pydantic.v1 import Field
from pydantic.v1 import condecimal
from pydantic.v1.types import NonNegativeInt

from pcapi.core.offers import models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pydantic import Field, ConfigDict
from decimal import Decimal
from typing_extensions import Annotated


logger = logging.getLogger(__name__)


class StocksResponseModel(BaseModel):
    stocks_count: int
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={datetime: format_into_utc_date})


class StockCreationBodyModel(BaseModel):
    activation_codes: list[str] | None
    activation_codes_expiration_datetime: datetime | None
    beginning_datetime: datetime | None
    booking_limit_datetime: datetime | None
    price: decimal.Decimal | None
    price_category_id: int | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(alias_generator=to_camel, json_encoders={datetime: format_into_utc_date}, extra="forbid")


class StockEditionBodyModel(BaseModel):
    beginning_datetime: datetime | None
    booking_limit_datetime: datetime | None
    id: int
    price: decimal.Decimal | None
    price_category_id: int | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)
    model_config = ConfigDict(alias_generator=to_camel, extra="forbid")


class StockIdResponseModel(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True)


class StocksUpsertBodyModel(BaseModel):
    offer_id: int
    if typing.TYPE_CHECKING:
        stocks: list[StockCreationBodyModel | StockEditionBodyModel]
    else:
        stocks: pydantic_v1.conlist(
            StockCreationBodyModel | StockEditionBodyModel, min_items=1, max_items=models.Offer.MAX_STOCKS_PER_OFFER
        )
    model_config = ConfigDict(alias_generator=to_camel)


class UpdateVenueStockBodyModel(BaseModel):
    """Available stock quantity for a book"""

    ref: str = Field(title="ISBN", description="Format: EAN13")
    available: NonNegativeInt
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        price: decimal.Decimal
    else:
        price: Annotated[Decimal, Field(gt=0, decimal_places=2)]
    model_config = ConfigDict(title="Stock")


class UpdateVenueStocksBodyModel(BaseModel):
    stocks: list[UpdateVenueStockBodyModel]
    model_config = ConfigDict(title="Venue's stocks update body")
