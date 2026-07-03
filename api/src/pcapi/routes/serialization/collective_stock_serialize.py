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
from pcapi.serialization.utils import DecimalPrice


def validate_booking_limit_datetime(booking_limit_datetime: datetime, info: pydantic_v2.ValidationInfo) -> datetime:
    start_datetime = info.data.get("startDatetime")
    if start_datetime and booking_limit_datetime > start_datetime:
        raise PydanticError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")

    return booking_limit_datetime


def validate_start_datetime(start_datetime: datetime) -> datetime:
    if start_datetime < datetime.now(timezone.utc):
        raise PydanticError("L'évènement ne peut commencer dans le passé.")
    return start_datetime


def validate_end_datetime(end_datetime: datetime, info: pydantic_v2.ValidationInfo) -> datetime:
    if end_datetime < datetime.now(timezone.utc):
        raise PydanticError("L'évènement ne peut se terminer dans le passé.")

    start_datetime = info.data.get("startDatetime")
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
    amount: DecimalPrice = pydantic_v2.Field(ge=0)

    @pydantic_v2.model_validator(mode="after")
    def validate_model(self) -> typing.Self:
        if self.label is not None and self.type != models.CollectiveAdditionalFeeType.OTHER:
            raise_error_from_location(None, loc="label", msg="Le label ne peut pas être rempli pour ce type")

        if self.label is None and self.type == models.CollectiveAdditionalFeeType.OTHER:
            raise_error_from_location(None, loc="label", msg="Le label doit être rempli pour ce type")

        return self


def _validate_total_price(
    price: decimal.Decimal, service_price: decimal.Decimal, additional_fees: list[CollectiveAdditionalFeeModel]
) -> None:
    # check additional fees type and label duplicates
    if additional_fees:
        type_counter = collections.Counter(
            fee.type for fee in additional_fees if fee.type != models.CollectiveAdditionalFeeType.OTHER
        )
        if any(type_count > 1 for type_count in type_counter.values()):
            raise_error_from_location(None, loc="collectiveAdditionalFees.root", msg="Un type est en doublon")

        label_counter = collections.Counter(
            fee.label for fee in additional_fees if fee.type == models.CollectiveAdditionalFeeType.OTHER
        )
        if any(label_count > 1 for label_count in label_counter.values()):
            raise_error_from_location(None, loc="collectiveAdditionalFees.root", msg="Un label est en doublon")

    # check total price
    total_price = service_price + sum(fee.amount for fee in additional_fees)
    if total_price != price:
        raise_error_from_location(
            None,
            loc="price",
            msg="Le prix total ne correspond pas à la somme du prix de la prestation et des frais annexes",
        )

    if total_price > settings.EAC_OFFER_PRICE_LIMIT:
        raise_error_from_location(None, loc="price", msg="Le prix est trop élevé")


class CollectiveStockCreationBodyModel(HttpBodyModel):
    offerId: int
    startDatetime: typing.Annotated[datetime, pydantic_v2.AfterValidator(validate_start_datetime)]
    endDatetime: typing.Annotated[datetime, pydantic_v2.AfterValidator(validate_end_datetime)]
    bookingLimitDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_booking_limit_datetime)]
    price: DecimalPrice = pydantic_v2.Field(ge=0, le=settings.EAC_OFFER_PRICE_LIMIT)
    servicePrice: DecimalPrice | None = pydantic_v2.Field(default=None, ge=0)
    collectiveAdditionalFees: list[CollectiveAdditionalFeeModel] | None = pydantic_v2.Field(
        default=None, max_length=constants.MAX_COLLECTIVE_NUMBER_OF_ADDITIONAL_FEES
    )
    numberOfTickets: int = pydantic_v2.Field(ge=0, le=settings.EAC_NUMBER_OF_TICKETS_LIMIT)
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

        # numberOfTeachers, servicePrice, collectiveAdditionalFees must be present and not None only when FF is ON
        for field_name, field_value in (
            ("numberOfTeachers", self.numberOfTeachers),
            ("servicePrice", self.servicePrice),
            ("collectiveAdditionalFees", self.collectiveAdditionalFees),
        ):
            if new_price_ff_is_active and field_value is None:
                raise_error_from_location(None, loc=field_name, msg="Ce champ est requis")

            if not new_price_ff_is_active and field_name in self.model_fields_set:
                raise_error_from_location(None, loc=field_name, msg="Ce champ ne peut pas être présent")

        if new_price_ff_is_active:
            assert self.servicePrice is not None  # checked above when ff is active
            assert self.collectiveAdditionalFees is not None  # same

            _validate_total_price(
                price=self.price, service_price=self.servicePrice, additional_fees=self.collectiveAdditionalFees
            )

        return self


class CollectiveStockEditionBodyModel(HttpBodyModel):
    startDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_start_datetime)] = None
    endDatetime: typing.Annotated[datetime | None, pydantic_v2.AfterValidator(validate_end_datetime)] = None
    bookingLimitDatetime: typing.Annotated[
        datetime | None, pydantic_v2.AfterValidator(validate_booking_limit_datetime)
    ] = None
    price: DecimalPrice | None = pydantic_v2.Field(default=None, ge=0, le=settings.EAC_OFFER_PRICE_LIMIT)
    servicePrice: DecimalPrice | None = pydantic_v2.Field(default=None, ge=0)
    collectiveAdditionalFees: list[CollectiveAdditionalFeeModel] | None = pydantic_v2.Field(
        default=None, max_length=constants.MAX_COLLECTIVE_NUMBER_OF_ADDITIONAL_FEES
    )
    numberOfTickets: int | None = pydantic_v2.Field(default=None, ge=0, le=settings.EAC_NUMBER_OF_TICKETS_LIMIT)
    numberOfTeachers: int | None = pydantic_v2.Field(default=None, ge=0, le=constants.MAX_COLLECTIVE_NUMBER_OF_TEACHERS)
    priceDetail: typing.Annotated[str | None, pydantic_v2.AfterValidator(validate_price_detail)] = None

    NON_NULLABLE_FIELDS: typing.ClassVar = (
        "startDatetime",
        "endDatetime",
        "bookingLimitDatetime",
        "price",
        "servicePrice",
        "collectiveAdditionalFees",
        "numberOfTickets",
        "numberOfTeachers",
    )

    @pydantic_v2.field_validator(*NON_NULLABLE_FIELDS, mode="before")
    @classmethod
    def validate_not_none(cls, value: typing.Any) -> typing.Any:
        if value is None:
            raise PydanticError("Ce champ ne peut pas être null")

        return value

    @pydantic_v2.model_validator(mode="after")
    def validate_model(self) -> typing.Self:
        new_price_ff_is_active = feature.FeatureToggle.WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS.is_active()

        # priceDetail must not be present when FF is ON
        if new_price_ff_is_active and "priceDetail" in self.model_fields_set:
            raise_error_from_location(None, loc="priceDetail", msg="Ce champ ne peut pas être édité")

        if not new_price_ff_is_active:
            # these fields must not be present when FF is OFF
            for field_name in ("numberOfTeachers", "servicePrice", "collectiveAdditionalFees"):
                if field_name in self.model_fields_set:
                    raise_error_from_location(None, loc=field_name, msg="Ce champ ne peut pas être édité")

        if new_price_ff_is_active:
            # price, servicePrice and collectiveAdditionalFees must all be present or all absent
            updated_count = len({"price", "servicePrice", "collectiveAdditionalFees"} - self.model_fields_set)
            if updated_count not in (0, 3):
                raise_error_from_location(
                    None,
                    loc="price",
                    msg="Les champs price, servicePrice et collectiveAdditionalFees doivent tous être modifiés simultanément",
                )

            if self.price is not None and self.servicePrice is not None and self.collectiveAdditionalFees is not None:
                _validate_total_price(
                    price=self.price, service_price=self.servicePrice, additional_fees=self.collectiveAdditionalFees
                )

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
