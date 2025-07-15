import datetime
import typing

import pydantic.v1 as pydantic_v1

from pcapi.routes import serialization as routes_serialization
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.individual_offers.v1 import serialization as v1_serialization
from pcapi.serialization import utils as serialization_utils


def _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates(cls: typing.Any, values: dict) -> dict:
    stock: StockCreation | StockEdition | None = values.get("stock")
    publication_datetime: datetime.datetime | None = values.get("publication_datetime")
    booking_allowed_datetime: datetime.datetime | None = values.get("booking_allowed_datetime")

    if not stock or not stock.booking_limit_datetime:
        return values

    if publication_datetime and stock.booking_limit_datetime < publication_datetime:
        raise ValueError("`stock.bookingLimitDatetime` must be after `publicationDatetime`")

    if booking_allowed_datetime and stock.booking_limit_datetime < booking_allowed_datetime:
        raise ValueError("`stock.bookingLimitDatetime` must be after `bookingAllowedDatetime`")

    return values


class StockEdition(v1_serialization.BaseStockEdition):
    price: v1_serialization.offer_price_model | None = fields.PRICE


class StockCreation(v1_serialization.BaseStockCreation):
    price: v1_serialization.offer_price_model = fields.PRICE
    booking_limit_datetime: datetime.datetime | None = fields.BOOKING_LIMIT_DATETIME
    quantity: pydantic_v1.PositiveInt | v1_serialization.UNLIMITED_LITERAL | None = fields.QUANTITY  # type: ignore[assignment]

    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")

    @pydantic_v1.validator("price")
    def price_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be positive")
        return value


class StockUpsert(StockCreation):
    quantity: pydantic_v1.StrictInt | v1_serialization.UNLIMITED_LITERAL | None = fields.QUANTITY


class ProductOfferEdition(v1_serialization.OfferEditionBase):
    offer_id: int
    category_related_fields: v1_serialization.product_category_edition_fields | None = pydantic_v1.Field(
        None,
        description="To override category related fields, the category must be specified, even if it cannot be changed. Other category related fields may be left undefined to keep their current value.",
    )
    stock: StockEdition | None = fields.STOCK_EDITION
    name: v1_serialization.OfferName | None = fields.OFFER_NAME
    description: str | None = fields.OFFER_DESCRIPTION_WITH_MAX_LENGTH
    enable_double_bookings: bool | None = fields.OFFER_ENABLE_DOUBLE_BOOKINGS_ENABLED

    _validate_stock_booking_limit_datetime = pydantic_v1.root_validator(skip_on_failure=True, allow_reuse=True)(
        _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates
    )


class ProductOfferCreation(v1_serialization.OfferCreationBase):
    category_related_fields: v1_serialization.product_category_creation_fields
    stock: StockCreation | None
    location: (
        v1_serialization.PhysicalLocation | v1_serialization.DigitalLocation | v1_serialization.AddressLocation
    ) = fields.OFFER_LOCATION

    _validate_stock_booking_limit_datetime = pydantic_v1.root_validator(skip_on_failure=True, allow_reuse=True)(
        _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates
    )


class ProductOfferByEanCreation(routes_serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        ean: str = fields.EAN
    else:
        ean: pydantic_v1.constr(min_length=13, max_length=13) = fields.EAN
    stock: StockUpsert
    publication_datetime: datetime.datetime | serialization_utils.NOW_LITERAL | None = (
        fields.OFFER_PUBLICATION_DATETIME_WITH_DEFAULT
    )
    booking_allowed_datetime: datetime.datetime | None = fields.OFFER_BOOKING_ALLOWED_DATETIME

    _validate_publicationDatetime = serialization_utils.validate_datetime(
        "publication_datetime",
        always=True,  # to convert default literal `"now"` into an actual datetime
    )
    _validate_bookingAllowedDatetime = serialization_utils.validate_datetime("booking_allowed_datetime")
    _validate_stock_booking_limit_datetime = pydantic_v1.root_validator(skip_on_failure=True, allow_reuse=True)(
        _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates
    )

    class Config:
        extra = "forbid"


class ProductsOfferByEanCreation(routes_serialization.ConfiguredBaseModel):
    products: list[ProductOfferByEanCreation] = pydantic_v1.Field(
        description="List of product to create or update", max_items=500
    )
    location: (
        v1_serialization.PhysicalLocation | v1_serialization.DigitalLocation | v1_serialization.AddressLocation
    ) = fields.OFFER_LOCATION

    class Config:
        extra = "forbid"
