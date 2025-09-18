import decimal
import logging
from datetime import datetime
from datetime import timezone
from typing import Any

from pydantic.v1 import Field
from pydantic.v1 import validator
from pydantic.v1.fields import ModelField

from pcapi import settings
from pcapi.routes.serialization import ConfiguredBaseModel


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
    if booking_limit_datetime and values.get("startDatetime") and booking_limit_datetime > values["startDatetime"]:
        raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
    return booking_limit_datetime


def validate_start_datetime(start_datetime: datetime, values: dict[str, Any], field: ModelField) -> datetime:
    # we need a datetime with timezone information
    if start_datetime and start_datetime < datetime.now(timezone.utc):
        raise ValueError("L'évènement ne peut commencer dans le passé.")
    return start_datetime


def validate_end_datetime(end_datetime: datetime, values: dict[str, Any], field: ModelField) -> datetime:
    # we need a datetime with timezone information
    start_datetime = values.get("startDatetime")
    if end_datetime and end_datetime < datetime.now(timezone.utc):
        raise ValueError("L'évènement ne peut se terminer dans le passé.")
    if start_datetime and end_datetime < start_datetime:
        raise ValueError("La date de fin de l'évènement ne peut précéder la date de début.")
    return end_datetime


def validate_price_detail(educational_price_detail: str | None) -> str | None:
    if educational_price_detail and len(educational_price_detail) > 1000:
        raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
    return educational_price_detail


def number_of_tickets_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_number_of_tickets)


def start_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_start_datetime)


def end_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_end_datetime)


def price_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_price)


def booking_limit_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_booking_limit_datetime)


def price_detail_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_price_detail)


class CollectiveStockCreationBodyModel(ConfiguredBaseModel):
    offerId: int
    startDatetime: datetime
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    totalPrice: decimal.Decimal
    numberOfTickets: int
    educationalPriceDetail: str | None

    _validate_number_of_tickets = number_of_tickets_validator("numberOfTickets")
    _validate_total_price = price_validator("totalPrice")
    _validate_start_datetime = start_datetime_validator("startDatetime")
    _validate_end_datetime = end_datetime_validator("endDatetime")
    _validate_booking_limit_datetime = booking_limit_datetime_validator("bookingLimitDatetime")
    _validate_educational_price_detail = price_detail_validator("educationalPriceDetail")

    class Config:
        extra = "forbid"


class CollectiveStockEditionBodyModel(ConfiguredBaseModel):
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float | None = Field(alias="totalPrice")
    numberOfTickets: int | None
    educationalPriceDetail: str | None

    _validate_number_of_tickets = number_of_tickets_validator("numberOfTickets")
    _validate_total_price = price_validator("price")
    _validate_educational_price_detail = price_detail_validator("educationalPriceDetail")
    _validate_booking_limit_datetime = booking_limit_datetime_validator("bookingLimitDatetime")

    @validator("endDatetime")
    def validate_end_datetime(
        cls, end_datetime: datetime | None, values: dict[str, Any], field: ModelField
    ) -> datetime | None:
        if end_datetime is None:
            raise ValueError("La date de fin de l'évènement ne peut pas être nulle.")

        validate_end_datetime(end_datetime, values, field)
        return end_datetime

    @validator("startDatetime")
    def validate_start_datetime(
        cls, start_datetime: datetime | None, values: dict[str, Any], field: ModelField
    ) -> datetime | None:
        if start_datetime is None:
            raise ValueError("La date de début de l'évènement ne peut pas être nulle.")

        validate_start_datetime(start_datetime, values, field)
        return start_datetime

    class Config:
        extra = "forbid"


class CollectiveStockResponseModel(ConfiguredBaseModel):
    id: int
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float
    numberOfTickets: int | None
    priceDetail: str | None = Field(alias="educationalPriceDetail")
