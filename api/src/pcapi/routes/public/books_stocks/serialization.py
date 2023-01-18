from datetime import datetime
import decimal
import logging
import typing

import pydantic
from pydantic import Field
from pydantic import condecimal
from pydantic.types import NonNegativeInt

from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Stock
from pcapi.models.feature import FeatureToggle
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import dehumanize_or_raise


logger = logging.getLogger(__name__)


class StockResponseModel(BaseModel):
    activationCodesExpirationDatetime: datetime | None
    hasActivationCodes: bool
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    dnBookedQuantity: int = Field(alias="bookingsQuantity")
    dateCreated: datetime
    dateModified: datetime
    id: str
    isEventDeletable: bool
    isEventExpired: bool
    offerId: str
    price: float
    quantity: int | None

    _humanize_id = humanize_field("id")
    _humanize_offer_id = humanize_field("offerId")

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
    price: float
    quantity: int | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class StockEditionBodyModel(BaseModel):
    beginning_datetime: datetime | None
    booking_limit_datetime: datetime | None
    humanized_id: str
    price: float
    quantity: int | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"

    @property
    def id(self) -> int:
        return dehumanize_or_raise(self.humanized_id)


class StockIdResponseModel(BaseModel):
    id: str

    _humanize_stock_id = humanize_field("id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class EducationalStockIdResponseModel(BaseModel):
    id: str
    collectiveOfferTemplateId: str

    _humanize_stock_id = humanize_field("id")
    _humanize_collective_offer_template_id = humanize_field("collectiveOfferTemplateId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class StocksUpsertBodyModel(BaseModel):
    humanized_offer_id: str
    stocks: list[StockCreationBodyModel | StockEditionBodyModel]

    class Config:
        alias_generator = to_camel

    @property
    def offer_id(self) -> int:
        return dehumanize_or_raise(self.humanized_offer_id)


class UpdateVenueStockBodyModel(BaseModel):
    """Available stock quantity for a book"""

    ref: str = Field(title="ISBN", description="Format: EAN13")
    available: NonNegativeInt
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        price: decimal.Decimal
    else:
        price: condecimal(decimal_places=2) = Field(
            None,
            description="(Requis à partir du 10/12/2022) Prix en Euros avec 2 décimales possibles",
        )

    @pydantic.validator("price", pre=True)
    def empty_string_price_casted_to_none(cls, v):  # type: ignore [no-untyped-def]
        if FeatureToggle.WIP_REQUIRE_PRICE_IN_STOCK_API.is_active():
            return v  # do nothing if flag is on, let `require_price()` do the job
        # Performed before Pydantic validators to catch empty strings but will not get "0"
        if not v:
            return None
        return v

    @pydantic.validator("price")
    def zero_price_casted_to_none(cls, v):  # type: ignore [no-untyped-def]
        if FeatureToggle.WIP_REQUIRE_PRICE_IN_STOCK_API.is_active():
            return v  # do nothing if flag is on, let `require_price()` do the job
        # Performed before Pydantic validators to catch empty strings but will not get "0"
        if not v:
            return None
        return v

    @pydantic.root_validator
    def require_price(cls, values: dict) -> dict:
        if not FeatureToggle.WIP_REQUIRE_PRICE_IN_STOCK_API.is_active():
            return values  # do nothing if flag is off, let validators above do the job
        price = values.get("price")
        if not price:
            # FIXME (dbaty: 2022-11-30): remove this warning around
            # february 2023 when we're sure that all providers provide
            # the price.
            logger.warning("Provider sent stock without price")
            raise ValueError("Le prix est obligatoire depuis le 10/12/2022")
        return values

    class Config:
        title = "Stock"


class UpdateVenueStocksBodyModel(BaseModel):
    stocks: list[UpdateVenueStockBodyModel]

    class Config:
        title = "Venue's stocks update body"
