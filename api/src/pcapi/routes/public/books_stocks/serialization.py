from datetime import datetime
import decimal
import logging
import typing

from pydantic.v1 import Field
from pydantic.v1 import condecimal
from pydantic.v1.types import NonNegativeInt

from pcapi.core.offers import models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class StockCreationBodyModel(BaseModel):
    activation_codes: list[str] | None
    activation_codes_expiration_datetime: datetime | None
    beginning_datetime: datetime | None
    booking_limit_datetime: datetime | None
    price: decimal.Decimal | None
    price_category_id: int | None
    quantity: int | None = Field(None, ge=0, le=models.Stock.MAX_STOCK_QUANTITY)

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

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class UpdateVenueStockBodyModel(BaseModel):
    """Available stock quantity for a book"""

    ref: str = Field(title="ISBN", description="Format: EAN13")
    available: NonNegativeInt
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        price: decimal.Decimal
    else:
        price: condecimal(gt=0, decimal_places=2)

    class Config:
        title = "Stock"


class UpdateVenueStocksBodyModel(BaseModel):
    stocks: list[UpdateVenueStockBodyModel]

    class Config:
        title = "Venue's stocks update body"
