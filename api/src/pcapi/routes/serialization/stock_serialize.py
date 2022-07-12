from datetime import datetime

from pydantic import Field
from pydantic import condecimal
from pydantic import validator
from pydantic.types import NonNegativeInt

from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers.models import ActivationCode
from pcapi.core.offers.models import Stock
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


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
    numberOfTickets: int | None
    isEducationalStockEditable: bool | None
    educationalPriceDetail: str | None

    _humanize_id = humanize_field("id")
    _humanize_offer_id = humanize_field("offerId")

    @classmethod
    def from_orm(cls, stock: Stock):  # type: ignore
        activation_code = (
            ActivationCode.query.filter(ActivationCode.stockId == stock.id).first()
            if stock.canHaveActivationCodes
            else None
        )
        stock.hasActivationCodes = bool(activation_code)
        stock.activationCodesExpirationDatetime = activation_code.expirationDate if activation_code else None
        stock.isEducationalStockEditable = False
        if stock.offer.isEducational:
            stock.isEducationalStockEditable = all(
                booking.status in (BookingStatus.PENDING, BookingStatus.CANCELLED) for booking in stock.bookings
            )
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
    id: int
    price: float
    quantity: int | None

    _dehumanize_id = dehumanize_field("id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


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
    offer_id: int
    stocks: list[StockCreationBodyModel | StockEditionBodyModel]

    _dehumanize_offer_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel


class StockIdsResponseModel(BaseModel):
    stockIds: list[StockIdResponseModel]


class UpdateVenueStockBodyModel(BaseModel):
    """Available stock quantity for a book"""

    ref: str = Field(title="ISBN", description="Format: EAN13")
    available: NonNegativeInt
    price: condecimal(decimal_places=2) = Field(  # type: ignore [valid-type]
        None, description="(Optionnel) Prix en Euros avec 2 décimales possibles"
    )

    @validator("price", pre=True)
    def empty_string_price_casted_to_none(cls, v):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        # Performed before Pydantic validators to catch empty strings but will not get "0"
        if not v:
            return None
        return v

    @validator("price")
    def zero_price_casted_to_none(cls, v):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        # Performed before Pydantic validators to catch empty strings but will not get "0"
        if not v:
            return None
        return v

    class Config:
        title = "Stock"


class UpdateVenueStocksBodyModel(BaseModel):
    stocks: list[UpdateVenueStockBodyModel]

    class Config:
        title = "Venue's stocks update body"
