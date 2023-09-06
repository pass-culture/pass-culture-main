from datetime import datetime
import decimal
import logging
import typing

import pydantic.v1 as pydantic_v1
from pydantic.v1 import Field
from pydantic.v1 import condecimal
from pydantic.v1.types import NonNegativeInt

from pcapi.core.offers import models
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Stock
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class StockResponseModel(BaseModel):
    activationCodesExpirationDatetime: datetime | None
    hasActivationCodes: bool
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    dnBookedQuantity: int = Field(alias="bookingsQuantity")
    dateCreated: datetime
    dateModified: datetime
    id: int
    isEventDeletable: bool
    isEventExpired: bool
    price: float
    quantity: int | None

    @classmethod
    def from_orm(cls, stock: Stock) -> "StockResponseModel":
        activation_code = (
            ActivationCode.query.filter(ActivationCode.stockId == stock.id).first()
            if stock.canHaveActivationCodes
            else None
        )
        stock.hasActivationCodes = bool(activation_code)
        stock.activationCodesExpirationDatetime = activation_code.expirationDate if activation_code else None
        return super().from_orm(stock)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True


class StocksResponseModel(BaseModel):
    stocks: list[StockResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


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


class StockIdResponseModel(BaseModel):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class StocksUpsertBodyModel(BaseModel):
    offer_id: int
    stocks: pydantic_v1.conlist(  # type: ignore
        StockCreationBodyModel | StockEditionBodyModel, min_items=1, max_items=models.Offer.MAX_STOCKS_PER_OFFER
    )

    class Config:
        alias_generator = to_camel


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
