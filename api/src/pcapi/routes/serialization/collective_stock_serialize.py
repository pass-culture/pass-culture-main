import typing
from datetime import datetime
from datetime import timezone

import pydantic as pydantic_v2
from pydantic.experimental.missing_sentinel import MISSING
from pydantic.json_schema import SkipJsonSchema

from pcapi import settings
from pcapi.routes.serialization import HttpBodyModel
from pcapi.serialization.exceptions import PydanticError


def validate_number_of_tickets(number_of_tickets: int | None) -> int:
    if number_of_tickets is None:
        raise PydanticError("Le nombre de places ne peut pas être nul.")
    if number_of_tickets < 0:
        raise PydanticError("Le nombre de places ne peut pas être négatif.")
    if number_of_tickets > settings.EAC_NUMBER_OF_TICKETS_LIMIT:
        raise PydanticError("Le nombre de places est trop élevé.")
    return number_of_tickets


def validate_price(price: float | None) -> float:
    if price is None:
        raise PydanticError("Le prix ne peut pas être nul.")
    if price < 0:
        raise PydanticError("Le prix ne peut pas être négatif.")
    if price > settings.EAC_OFFER_PRICE_LIMIT:
        raise PydanticError("Le prix est trop élevé.")
    return price


def validate_booking_limit_datetime(
    booking_limit_datetime: datetime | None, info: pydantic_v2.ValidationInfo
) -> datetime | None:
    start_datetime = info.data.get("startDatetime")
    if booking_limit_datetime and start_datetime and booking_limit_datetime > start_datetime:
        raise PydanticError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
    return booking_limit_datetime


def validate_start_datetime(start_datetime: datetime | None) -> datetime:
    if start_datetime is None:
        raise PydanticError("La date de début de l'évènement ne peut pas être nulle.")

    # we need a datetime with timezone information
    if start_datetime and start_datetime < datetime.now(timezone.utc):
        raise PydanticError("L'évènement ne peut commencer dans le passé.")
    return start_datetime


def validate_end_datetime(end_datetime: datetime | None, info: pydantic_v2.ValidationInfo) -> datetime:
    if end_datetime is None:
        raise PydanticError("La date de fin de l'évènement ne peut pas être nulle.")

    # we need a datetime with timezone information
    start_datetime = info.data.get("startDatetime")
    if end_datetime and end_datetime < datetime.now(timezone.utc):
        raise PydanticError("L'évènement ne peut se terminer dans le passé.")
    if start_datetime and end_datetime < start_datetime:
        raise PydanticError("La date de fin de l'évènement ne peut précéder la date de début.")
    return end_datetime


def validate_price_detail(educational_price_detail: str | None) -> str | None:
    if educational_price_detail and len(educational_price_detail) > 1000:
        raise PydanticError("Le détail du prix ne doit pas excéder 1000 caractères.")
    return educational_price_detail


class CollectiveStockCreationBodyModel(HttpBodyModel):
    offerId: int
    startDatetime: typing.Annotated[datetime, pydantic_v2.AfterValidator(validate_start_datetime)]
    endDatetime: typing.Annotated[datetime, pydantic_v2.AfterValidator(validate_end_datetime)]
    bookingLimitDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_booking_limit_datetime)]
    totalPrice: typing.Annotated[float, pydantic_v2.AfterValidator(validate_price)]
    numberOfTickets: typing.Annotated[int, pydantic_v2.AfterValidator(validate_number_of_tickets)]
    educationalPriceDetail: typing.Annotated[str | None, pydantic_v2.AfterValidator(validate_price_detail)]


class CollectiveStockEditionBodyModel(HttpBodyModel):
    # startDatetime -> non-required, nullable
    # frontend -> startDatetime?: (string | null);
    startDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_start_datetime)] = None
    # endDatetime -> non-required, non-nullable (in schema only)
    # frontend -> endDatetime?: string;
    endDatetime: typing.Annotated[
        datetime | SkipJsonSchema[None], pydantic_v2.AfterValidator(validate_end_datetime)
    ] = None
    # bookingLimitDatetime -> non-required, non-nullable
    # mypy error, experimental feature
    # frontend -> bookingLimitDatetime?: string;
    bookingLimitDatetime: typing.Annotated[
        datetime | MISSING, pydantic_v2.AfterValidator(validate_booking_limit_datetime)
    ] = MISSING
    price: typing.Annotated[float | None, pydantic_v2.AfterValidator(validate_price)] = pydantic_v2.Field(
        alias="totalPrice", default=None
    )
    numberOfTickets: typing.Annotated[int | None, pydantic_v2.AfterValidator(validate_number_of_tickets)] = None
    educationalPriceDetail: typing.Annotated[str | None, pydantic_v2.AfterValidator(validate_price_detail)] = None


class CollectiveStockResponseModel(HttpBodyModel):
    # id -> required, non-nullable
    # frontend -> id: number;
    id: int
    startDatetime: datetime
    endDatetime: datetime
    bookingLimitDatetime: datetime
    price: float
    numberOfTickets: int
    # priceDetail -> required, nullable
    # frontend -> educationalPriceDetail: (string | null);
    priceDetail: str | None = pydantic_v2.Field(alias="educationalPriceDetail")
