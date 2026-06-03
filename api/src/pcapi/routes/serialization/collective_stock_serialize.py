import typing
from datetime import datetime
from datetime import timezone

import pydantic as pydantic_v2

from pcapi import settings
from pcapi.core.educational import constants
from pcapi.core.educational import models
from pcapi.models import feature
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization.utils import raise_error_from_location
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


def validate_price_detail(price_detail: str | None) -> str | None:
    if price_detail and len(price_detail) > constants.MAX_COLLECTIVE_PRICE_DETAILS_LENGTH:
        raise PydanticError(
            f"Le détail du prix ne doit pas excéder {constants.MAX_COLLECTIVE_PRICE_DETAILS_LENGTH} caractères."
        )
    return price_detail


class CollectiveStockCreationBodyModel(HttpBodyModel):
    offerId: int
    startDatetime: typing.Annotated[datetime, pydantic_v2.AfterValidator(validate_start_datetime)]
    endDatetime: typing.Annotated[datetime, pydantic_v2.AfterValidator(validate_end_datetime)]
    bookingLimitDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_booking_limit_datetime)]
    price: typing.Annotated[float, pydantic_v2.AfterValidator(validate_price)]
    numberOfTickets: typing.Annotated[int, pydantic_v2.AfterValidator(validate_number_of_tickets)]
    priceDetail: typing.Annotated[str | None, pydantic_v2.AfterValidator(validate_price_detail)]


class CollectiveStockEditionBodyModel(HttpBodyModel):
    startDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_start_datetime)] = None
    endDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_end_datetime)] = None
    bookingLimitDatetime: typing.Annotated[
        datetime | None, pydantic_v2.AfterValidator(validate_booking_limit_datetime)
    ] = None
    price: typing.Annotated[float | None, pydantic_v2.AfterValidator(validate_price)] = pydantic_v2.Field(default=None)
    numberOfTickets: typing.Annotated[int | None, pydantic_v2.AfterValidator(validate_number_of_tickets)] = None
    priceDetail: typing.Annotated[str | None, pydantic_v2.AfterValidator(validate_price_detail)] = None

    @pydantic_v2.model_validator(mode="after")
    def validate_price_detail(self) -> typing.Self:
        if (
            feature.FeatureToggle.WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS.is_active()
            and "priceDetail" in self.model_fields_set
        ):
            raise_error_from_location(None, loc="priceDetail", msg="Ce champ ne peut pas être édité")

        return self


class CollectiveAdditionalFeeResponseModel(HttpBodyModel):
    type: models.CollectiveAdditionalFeeType
    label: str | None
    amount: float


class CollectiveStockResponseModel(HttpBodyModel):
    id: int
    startDatetime: datetime
    endDatetime: datetime
    bookingLimitDatetime: datetime
    price: float
    servicePrice: float | None
    collectiveAdditionalFees: list[CollectiveAdditionalFeeResponseModel]
    numberOfTickets: int
    numberOfTeachers: int
    priceDetail: str | None
