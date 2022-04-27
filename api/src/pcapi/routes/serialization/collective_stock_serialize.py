from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from pydantic import Field
from pydantic import validator

from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class CollectiveStockIdResponseModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


def validate_number_of_tickets(number_of_tickets: int) -> int:
    if number_of_tickets < 0:
        raise ValueError("Le nombre de places ne peut pas être négatif.")
    return number_of_tickets


def validate_price(price: float) -> float:
    if price < 0:
        raise ValueError("Le prix ne peut pas être négatif.")
    return price


def validate_booking_limit_datetime(
    booking_limit_datetime: Optional[datetime], values: Dict[str, Any]
) -> Optional[datetime]:
    if booking_limit_datetime and booking_limit_datetime > values["beginning_datetime"]:
        raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
    return booking_limit_datetime


def validate_price_detail(educational_price_detail: Optional[str]) -> Optional[str]:
    if educational_price_detail and len(educational_price_detail) > 1000:
        raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
    return educational_price_detail


def number_of_tickets_validator(field_name: str, pre: bool) -> classmethod:
    return validator(field_name, pre=pre, allow_reuse=True)(validate_number_of_tickets)


def price_validator(field_name: str, pre: bool) -> classmethod:
    return validator(field_name, pre=pre, allow_reuse=True)(validate_price)


def booking_limit_datetime_validator(field_name: str, pre: bool = False) -> classmethod:
    return validator(field_name, pre=pre, allow_reuse=True)(validate_booking_limit_datetime)


def price_detail_validator(field_name: str, pre: bool = False) -> classmethod:
    return validator(field_name, pre=pre, allow_reuse=True)(validate_price_detail)


class CollectiveStockCreationBodyModel(BaseModel):
    offer_id: int
    beginning_datetime: datetime
    booking_limit_datetime: Optional[datetime]
    total_price: float
    number_of_tickets: int
    educational_price_detail: Optional[str]

    _dehumanize_offer_id = dehumanize_field("offer_id")
    _validate_number_of_tickets = number_of_tickets_validator("number_of_tickets", pre=True)
    _validate_total_price = price_validator("total_price", pre=True)
    _validate_booking_limit_datetime = booking_limit_datetime_validator("booking_limit_datetime")
    _validate_educational_price_detail = price_detail_validator("educational_price_detail")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveStockResponseModel(BaseModel):
    id: str
    beginningDatetime: Optional[datetime]
    bookingLimitDatetime: Optional[datetime]
    price: float
    numberOfTickets: Optional[int]
    isEducationalStockEditable: Optional[bool]
    priceDetail: Optional[str] = Field(alias="educationalPriceDetail")
    stockId: Optional[str]

    _humanize_id = humanize_field("id")
    _humanize_stock_id = humanize_field("stockId")

    @classmethod
    def from_orm(cls, stock: CollectiveStock):  # type: ignore
        stock.isEducationalStockEditable = all(
            collective_booking.status in (CollectiveBookingStatus.PENDING, CollectiveBookingStatus.CANCELLED)
            for collective_booking in stock.collectiveBookings
        )
        return super().from_orm(stock)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
