import collections
import decimal
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


class CollectiveAdditionalFeeModel(HttpBodyModel):
    type: models.CollectiveAdditionalFeeType
    label: str | None
    amount: float

    @pydantic_v2.model_validator(mode="after")
    def validate_model(self) -> typing.Self:
        if self.label is not None and self.type != models.CollectiveAdditionalFeeType.OTHER:
            raise_error_from_location(None, loc="label", msg="Le label ne peut pas être rempli pour ce type")

        return self


class CollectiveStockCreationBodyModel(HttpBodyModel):
    offerId: int
    startDatetime: typing.Annotated[datetime, pydantic_v2.AfterValidator(validate_start_datetime)]
    endDatetime: typing.Annotated[datetime, pydantic_v2.AfterValidator(validate_end_datetime)]
    bookingLimitDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_booking_limit_datetime)]
    price: typing.Annotated[float, pydantic_v2.AfterValidator(validate_price)]
    servicePrice: float | None = pydantic_v2.Field(default=None, ge=0)
    additionalFees: list[CollectiveAdditionalFeeModel] | None = pydantic_v2.Field(
        default=None, max_length=constants.MAX_COLLECTIVE_NUMBER_OF_ADDITIONAL_FEES
    )
    numberOfTickets: typing.Annotated[int, pydantic_v2.AfterValidator(validate_number_of_tickets)]
    numberOfTeachers: int | None = pydantic_v2.Field(default=None, ge=0, le=constants.MAX_COLLECTIVE_NUMBER_OF_TEACHERS)
    priceDetail: typing.Annotated[str | None, pydantic_v2.AfterValidator(validate_price_detail)] = None

    @pydantic_v2.model_validator(mode="after")
    def validate_model(self) -> typing.Self:
        new_price_ff_is_active = feature.FeatureToggle.WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS.is_active()

        # priceDetail must be present only when FF is OFF
        if new_price_ff_is_active and "priceDetail" in self.model_fields_set:
            raise_error_from_location(None, loc="priceDetail", msg="Ce champ ne peut pas être présent")

        if not new_price_ff_is_active and "priceDetail" not in self.model_fields_set:
            raise_error_from_location(None, loc="priceDetail", msg="Ce champ est requis")

        # numberOfTeachers, servicePrice, additionalFees must be present and not None only when FF is ON
        for field_name, field_value in (
            ("numberOfTeachers", self.numberOfTeachers),
            ("servicePrice", self.servicePrice),
            ("additionalFees", self.additionalFees),
        ):
            if new_price_ff_is_active and field_value is None:
                raise_error_from_location(None, loc=field_name, msg="Ce champ est requis")

            if not new_price_ff_is_active and field_name in self.model_fields_set:
                raise_error_from_location(None, loc=field_name, msg="Ce champ ne peut pas être présent")

        if new_price_ff_is_active:
            # check additional fees type and label duplicates
            if self.additionalFees:
                type_counter = collections.Counter(
                    fee.type for fee in self.additionalFees if fee.type != models.CollectiveAdditionalFeeType.OTHER
                )
                if any(type_count > 1 for type_count in type_counter.values()):
                    raise_error_from_location(None, loc="additionalFees", msg="Un type est en doublon")

                label_counter = collections.Counter(
                    fee.label for fee in self.additionalFees if fee.type == models.CollectiveAdditionalFeeType.OTHER
                )
                if any(label_count > 1 for label_count in label_counter.values()):
                    raise_error_from_location(None, loc="additionalFees", msg="Un label est en doublon")

            # check total price
            assert self.servicePrice is not None  # checked above when ff is active
            assert self.additionalFees is not None  # same
            total_price = decimal.Decimal(self.servicePrice) + sum(
                decimal.Decimal(fee.amount) for fee in self.additionalFees
            )
            if total_price != decimal.Decimal(self.price):
                raise_error_from_location(None, loc="price", msg="Le prix total ne correspond pas à la somme des frais")

            if total_price > settings.EAC_OFFER_PRICE_LIMIT:
                raise_error_from_location(None, loc="price", msg="Le prix est trop élevé")

        return self


class CollectiveStockEditionBodyModel(HttpBodyModel):
    startDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_start_datetime)] = None
    endDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_end_datetime)] = None
    bookingLimitDatetime: typing.Annotated[
        datetime | None, pydantic_v2.AfterValidator(validate_booking_limit_datetime)
    ] = None
    price: typing.Annotated[float | None, pydantic_v2.AfterValidator(validate_price)] = pydantic_v2.Field(default=None)
    numberOfTickets: typing.Annotated[int | None, pydantic_v2.AfterValidator(validate_number_of_tickets)] = None
    numberOfTeachers: int | None = pydantic_v2.Field(default=None, ge=0, le=constants.MAX_COLLECTIVE_NUMBER_OF_TEACHERS)
    priceDetail: typing.Annotated[str | None, pydantic_v2.AfterValidator(validate_price_detail)] = None

    @pydantic_v2.model_validator(mode="after")
    def validate_model(self) -> typing.Self:
        new_price_ff_is_active = feature.FeatureToggle.WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS.is_active()

        # priceDetail must not be present when FF is ON
        if new_price_ff_is_active and "priceDetail" in self.model_fields_set:
            raise_error_from_location(None, loc="priceDetail", msg="Ce champ ne peut pas être édité")

        # numberOfTeachers must not be present when FF is OFF
        if not new_price_ff_is_active and "numberOfTeachers" in self.model_fields_set:
            raise_error_from_location(None, loc="numberOfTeachers", msg="Ce champ ne peut pas être édité")

        # numberOfTeachers must not be set as None when FF is ON
        if new_price_ff_is_active and "numberOfTeachers" in self.model_fields_set and self.numberOfTeachers is None:
            raise_error_from_location(None, loc="numberOfTeachers", msg="Ce champ est requis")

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
