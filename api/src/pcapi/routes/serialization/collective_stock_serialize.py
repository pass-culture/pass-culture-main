from datetime import datetime
from datetime import timezone
import logging
from typing import Any
from typing import Dict

from pydantic import Field
from pydantic import validator
from pydantic.fields import ModelField

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class CollectiveStockIdResponseModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


def validate_number_of_tickets(number_of_tickets: int | None) -> int:
    if number_of_tickets is None:
        raise ValueError("Le nombre de places ne peut pas être nul.")
    if number_of_tickets < 0:
        raise ValueError("Le nombre de places ne peut pas être négatif.")
    return number_of_tickets


def validate_price(price: float | None) -> float:
    if price is None:
        raise ValueError("Le prix ne peut pas être nul.")
    if price < 0:
        raise ValueError("Le prix ne peut pas être négatif.")
    return price


def validate_booking_limit_datetime(booking_limit_datetime: datetime | None, values: Dict[str, Any]) -> datetime | None:
    if (
        booking_limit_datetime
        and "beginning_datetime" in values
        and booking_limit_datetime > values["beginning_datetime"]
    ):
        raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
    return booking_limit_datetime


def validate_beginning_datetime(beginning_datetime: datetime, values: Dict[str, Any], field: ModelField) -> datetime:
    # we need a datetime with timezone information which is not provided by datetime.utcnow.
    if beginning_datetime < datetime.now(timezone.utc):  # pylint: disable=datetime-now
        raise ValueError("L'évènement ne peut commencer dans le passé.")
    return beginning_datetime


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


def beginning_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_beginning_datetime)


def price_detail_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_price_detail)


class CollectiveStockCreationBodyModel(BaseModel):
    offer_id: int
    beginning_datetime: datetime
    booking_limit_datetime: datetime | None
    total_price: float
    number_of_tickets: int
    educational_price_detail: str | None

    _dehumanize_offer_id = dehumanize_field("offer_id")
    _validate_number_of_tickets = number_of_tickets_validator("number_of_tickets")
    _validate_total_price = price_validator("total_price")
    _validate_beginning_datetime = beginning_datetime_validator("beginning_datetime")
    _validate_booking_limit_datetime = booking_limit_datetime_validator("booking_limit_datetime")
    _validate_educational_price_detail = price_detail_validator("educational_price_detail")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveStockEditionBodyModel(BaseModel):
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float | None = Field(alias="totalPrice")
    numberOfTickets: int | None
    educationalPriceDetail: str | None

    _validate_number_of_tickets = number_of_tickets_validator("numberOfTickets")
    _validate_total_price = price_validator("price")
    _validate_educational_price_detail = price_detail_validator("educationalPriceDetail")
    _validate_beginning_datetime = beginning_datetime_validator("beginningDatetime")

    # FIXME (cgaunet, 2022-04-28): Once edit_collective_stock is not used by legacy code,
    # we can use the same interface as for creation and thus reuse the validator defined above.
    @validator("bookingLimitDatetime")
    def validate_booking_limit_datetime(  # pylint: disable=no-self-argument
        cls, booking_limit_datetime: datetime | None, values: Dict[str, Any]
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
    @validator("beginningDatetime", pre=True)
    def validate_beginning_limit_datetime(  # pylint: disable=no-self-argument
        cls, beginningDatetime: datetime | None
    ) -> datetime | None:
        if beginningDatetime is None:
            raise ValueError("La date de début de l'événement ne peut pas être nulle.")
        return beginningDatetime

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveStockResponseModel(BaseModel):
    id: str
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float
    numberOfTickets: int | None
    priceDetail: str | None = Field(alias="educationalPriceDetail")
    isEditable: bool = Field(alias="isEducationalStockEditable")
    # FIXME (cgaunet, 2022-04-22): Remove this field once ENABLE_NEW_EAC_MODEL is activated
    stockId: str | None

    _humanize_id = humanize_field("id")
    _humanize_stock_id = humanize_field("stockId")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
