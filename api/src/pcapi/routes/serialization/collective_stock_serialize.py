from datetime import datetime
from datetime import timezone
import decimal
import logging
from typing import Any

from pydantic.v1 import Field
from pydantic.v1 import validator
from pydantic.v1.fields import ModelField

from pcapi import settings
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


def validate_number_of_tickets(number_of_tickets: int | None) -> int:
    if number_of_tickets is None:
        raise ValueError("Le nombre de places ne peut pas être nul.")
    if number_of_tickets < 0:
        raise ValueError("Le nombre de places ne peut pas être négatif.")
    if number_of_tickets > settings.EAC_NUMBER_OF_TICKETS_LIMIT:
        raise ValueError("Le nombre de places est trop élevé.")
    return number_of_tickets


def validate_price(price: float | None) -> float:
    if price is None:
        raise ValueError("Le prix ne peut pas être nul.")
    if price < 0:
        raise ValueError("Le prix ne peut pas être négatif.")
    if price > settings.EAC_OFFER_PRICE_LIMIT:
        raise ValueError("Le prix est trop élevé.")
    return price


def validate_booking_limit_datetime(booking_limit_datetime: datetime | None, values: dict[str, Any]) -> datetime | None:
    if booking_limit_datetime and "start_datetime" in values and booking_limit_datetime > values["start_datetime"]:
        raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
    return booking_limit_datetime


def validate_start_datetime(start_datetime: datetime, values: dict[str, Any], field: ModelField) -> datetime:
    # we need a datetime with timezone information which is not provided by datetime.utcnow.
    if start_datetime < datetime.now(timezone.utc):  # pylint: disable=datetime-now
        raise ValueError("L'évènement ne peut commencer dans le passé.")
    return start_datetime


def validate_end_datetime(end_datetime: datetime, values: dict[str, Any], field: ModelField) -> datetime:
    # we need a datetime with timezone information which is not provided by datetime.utcnow.
    if end_datetime < datetime.now(timezone.utc):  # pylint: disable=datetime-now
        raise ValueError("L'évènement ne peut se terminer dans le passé.")
    return end_datetime


def validate_price_detail(educational_price_detail: str | None) -> str | None:
    if educational_price_detail and len(educational_price_detail) > 1000:
        raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
    return educational_price_detail


def number_of_tickets_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_number_of_tickets)


def price_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_price)


def booking_limit_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_booking_limit_datetime)


def start_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_start_datetime)


def end_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_end_datetime)


def price_detail_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_price_detail)


class CollectiveStockCreationBodyModel(BaseModel):
    offer_id: int
    start_datetime: datetime
    end_datetime: datetime
    booking_limit_datetime: datetime | None
    total_price: decimal.Decimal
    number_of_tickets: int
    educational_price_detail: str | None

    _validate_number_of_tickets = number_of_tickets_validator("number_of_tickets")
    _validate_total_price = price_validator("total_price")
    _validate_start_datetime = start_datetime_validator("start_datetime")
    _validate_end_datetime = end_datetime_validator("end_datetime")
    _validate_booking_limit_datetime = booking_limit_datetime_validator("booking_limit_datetime")
    _validate_educational_price_detail = price_detail_validator("educational_price_detail")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveStockEditionBodyModel(BaseModel):
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float | None = Field(alias="totalPrice")
    numberOfTickets: int | None
    educationalPriceDetail: str | None

    _validate_number_of_tickets = number_of_tickets_validator("numberOfTickets")
    _validate_total_price = price_validator("price")
    _validate_educational_price_detail = price_detail_validator("educationalPriceDetail")
    _validate_start_datetime = start_datetime_validator("startDatetime")
    _validate_end_datetime = end_datetime_validator("endDatetime")

    # FIXME (cgaunet, 2022-04-28): Once edit_collective_stock is not used by legacy code,
    # we can use the same interface as for creation and thus reuse the validator defined above.
    @validator("bookingLimitDatetime")
    def validate_booking_limit_datetime(
        cls, booking_limit_datetime: datetime | None, values: dict[str, Any]
    ) -> datetime | None:
        if (
            booking_limit_datetime
            and values.get("beginningDatetime", None) is not None
            and booking_limit_datetime > values["beginningDatetime"]
        ):
            raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
        return booking_limit_datetime

    # FIXME (cgaunet, 2022-04-28): Once edit_collective_stock is not used by legacy code,
    # we can use the same interface as for creation and thus reuse the validator defined above.
    @validator("endDatetime", pre=True)
    def validate_end_limit_datetime(cls, endDatetime: datetime | None) -> datetime | None:
        if endDatetime is None:
            raise ValueError("La date de fin de l'évènement ne peut pas être nulle.")
        return endDatetime

    # FIXME (cgaunet, 2022-04-28): Once edit_collective_stock is not used by legacy code,
    # we can use the same interface as for creation and thus reuse the validator defined above.
    @validator("startDatetime", pre=True)
    def validate_start_limit_datetime(cls, startDatetime: datetime | None) -> datetime | None:
        if startDatetime is None:
            raise ValueError("La date de début de l'évènement ne peut pas être nulle.")
        return startDatetime

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveStockResponseModel(BaseModel):
    id: int
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float
    numberOfTickets: int | None
    priceDetail: str | None = Field(alias="educationalPriceDetail")
    isEditable: bool = Field(alias="isEducationalStockEditable")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
