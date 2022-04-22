from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

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
    activationCodesExpirationDatetime: Optional[datetime]
    hasActivationCodes: bool
    beginningDatetime: Optional[datetime]
    bookingLimitDatetime: Optional[datetime]
    dnBookedQuantity: int = Field(alias="bookingsQuantity")
    dateCreated: datetime
    dateModified: datetime
    id: str
    isEventDeletable: bool
    isEventExpired: bool
    offerId: str
    price: float
    quantity: Optional[int]
    numberOfTickets: Optional[int]
    isEducationalStockEditable: Optional[bool]
    educationalPriceDetail: Optional[str]

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


class StockEditionResponseModel(BaseModel):
    beginningDatetime: datetime
    bookingLimitDatetime: datetime
    id: str
    price: float
    numberOfTickets: Optional[int]
    isEducationalStockEditable: bool
    educationalPriceDetail: Optional[str]

    _humanize_id = humanize_field("id")

    @classmethod
    def from_orm(cls, stock: Stock):  # type: ignore
        stock.isEducationalStockEditable = False
        if stock.offer.isEducational:
            stock.isEducationalStockEditable = all(
                booking.status in (BookingStatus.PENDING, BookingStatus.CANCELLED) for booking in stock.bookings
            )
        return super().from_orm(stock)

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True


class PatchShadowStockIntoEducationalStockResponseModel(StockEditionResponseModel):
    offerId: str

    class Config:
        orm_mode = True


class StockCreationBodyModel(BaseModel):
    activation_codes: Optional[list[str]]
    activation_codes_expiration_datetime: Optional[datetime]
    beginning_datetime: Optional[datetime]
    booking_limit_datetime: Optional[datetime]
    price: float
    quantity: Optional[int]

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class EducationalStockCreationBodyModel(BaseModel):
    offer_id: int
    beginning_datetime: datetime
    booking_limit_datetime: Optional[datetime]
    total_price: float
    number_of_tickets: int
    educational_price_detail: Optional[str]

    _dehumanize_id = dehumanize_field("offer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"

    @validator("number_of_tickets", pre=True)
    def validate_number_of_tickets(cls, number_of_tickets: int) -> int:  # pylint: disable=no-self-argument
        if number_of_tickets < 0:
            raise ValueError("Le nombre de places ne peut pas être négatif.")
        return number_of_tickets

    @validator("total_price", pre=True)
    def validate_price(cls, price: float) -> float:  # pylint: disable=no-self-argument
        if price < 0:
            raise ValueError("Le prix ne peut pas être négatif.")
        return price

    @validator("booking_limit_datetime")
    def validate_booking_limit_datetime(  # pylint: disable=no-self-argument
        cls, booking_limit_datetime: Optional[datetime], values: Dict[str, Any]
    ) -> Optional[datetime]:
        if booking_limit_datetime and booking_limit_datetime > values["beginning_datetime"]:
            raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
        return booking_limit_datetime

    @validator("educational_price_detail")
    def validate_price_detail(  # pylint: disable=no-self-argument
        cls, educational_price_detail: Optional[str]
    ) -> Optional[str]:
        if educational_price_detail and len(educational_price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return educational_price_detail


class EducationalStockEditionBodyModel(BaseModel):
    beginningDatetime: Optional[datetime]
    bookingLimitDatetime: Optional[datetime]
    price: Optional[float] = Field(alias="totalPrice")
    numberOfTickets: Optional[int]
    educationalPriceDetail: Optional[str]

    class Config:
        extra = "forbid"

    @validator("beginningDatetime", pre=True)
    def validate_beginning_datetime(cls, beginning_datetime):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if beginning_datetime is None:
            raise ValueError("La date d’évènement ne peut être nulle")
        return beginning_datetime

    @validator("numberOfTickets", pre=True)
    def validate_number_of_tickets(cls, number_of_tickets):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if number_of_tickets is None:
            raise ValueError("Le nombre de places ne peut être nul")
        if number_of_tickets < 0:
            raise ValueError("Le nombre de places ne peut pas être négatif.")
        return number_of_tickets

    @validator("price", pre=True)
    def validate_price(cls, price):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if price is None:
            raise ValueError("Le prix ne peut être nul")
        if price < 0:
            raise ValueError("Le prix ne peut pas être négatif.")
        return price

    @validator("bookingLimitDatetime")
    def validate_booking_limit_datetime(cls, booking_limit_datetime, values):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if (
            all([booking_limit_datetime, values["beginningDatetime"]])
            and booking_limit_datetime > values["beginningDatetime"]
        ):
            raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
        return booking_limit_datetime

    @validator("educationalPriceDetail")
    def validate_educational_price_detail(cls, educational_price_detail):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if len(educational_price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return educational_price_detail


class StockEditionBodyModel(BaseModel):
    beginning_datetime: Optional[datetime]
    booking_limit_datetime: Optional[datetime]
    id: int
    price: float
    quantity: Optional[int]

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


class StocksUpsertBodyModel(BaseModel):
    offer_id: int
    stocks: list[Union[StockCreationBodyModel, StockEditionBodyModel]]

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
