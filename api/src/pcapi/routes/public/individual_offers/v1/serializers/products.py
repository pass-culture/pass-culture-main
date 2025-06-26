import datetime
import typing

import pydantic.v1 as pydantic_v1

from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.individual_offers.v1 import serialization as v1_serialization


def _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates(cls: typing.Any, values: dict) -> dict:
    stock: v1_serialization.StockCreation | v1_serialization.StockEdition | None = values.get("stock")
    publication_datetime: datetime.datetime | None = values.get("publication_datetime")
    booking_allowed_datetime: datetime.datetime | None = values.get("booking_allowed_datetime")

    if not stock or not stock.booking_limit_datetime:
        return values

    if publication_datetime and stock.booking_limit_datetime < publication_datetime:
        raise ValueError("`stock.bookingLimitDatetime` must be after `publicationDatetime`")

    if booking_allowed_datetime and stock.booking_limit_datetime < booking_allowed_datetime:
        raise ValueError("`stock.bookingLimitDatetime` must be after `bookingAllowedDatetime`")

    return values


class ProductOfferEdition(v1_serialization.OfferEditionBase):
    offer_id: int
    category_related_fields: v1_serialization.product_category_edition_fields | None = pydantic_v1.Field(
        None,
        description="To override category related fields, the category must be specified, even if it cannot be changed. Other category related fields may be left undefined to keep their current value.",
    )
    stock: v1_serialization.StockEdition | None = fields.STOCK_EDITION
    name: v1_serialization.OfferName | None = fields.OFFER_NAME
    description: str | None = fields.OFFER_DESCRIPTION_WITH_MAX_LENGTH
    enable_double_bookings: bool | None = fields.OFFER_ENABLE_DOUBLE_BOOKINGS_ENABLED

    _validate_stock_booking_limit_datetime = pydantic_v1.root_validator(skip_on_failure=True, allow_reuse=True)(
        _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates
    )


class ProductOfferCreation(v1_serialization.OfferCreationBase):
    category_related_fields: v1_serialization.product_category_creation_fields
    stock: v1_serialization.StockCreation | None
    location: (
        v1_serialization.PhysicalLocation | v1_serialization.DigitalLocation | v1_serialization.AddressLocation
    ) = fields.OFFER_LOCATION

    _validate_stock_booking_limit_datetime = pydantic_v1.root_validator(skip_on_failure=True, allow_reuse=True)(
        _validate_stock_booking_limit_datetime_is_coherent_with_offer_dates
    )
