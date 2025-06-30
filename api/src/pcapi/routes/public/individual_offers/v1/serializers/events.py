import datetime
import decimal
import typing

import pydantic.v1 as pydantic_v1
from pydantic.v1.utils import GetterDict

from pcapi.core.categories import subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import models as offers_models
from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.individual_offers.v1 import base_serialization
from pcapi.routes.public.individual_offers.v1 import serialization as v1_serialization
from pcapi.routes.public.serialization.utils import StrEnum
from pcapi.serialization import utils as serialization_utils


EventCategoryEnum = StrEnum(  # type: ignore[call-overload]
    "CategoryEnum", {subcategory_id: subcategory_id for subcategory_id in subcategories.EVENT_SUBCATEGORIES}
)


class DecimalPriceGetterDict(GetterDict):
    def get(self, key: str, default: typing.Any | None = None) -> typing.Any:
        if key == "price" and isinstance(self._obj.price, decimal.Decimal):
            return finance_utils.to_cents(self._obj.price)
        return super().get(key, default)


class PriceCategoryCreation(serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        label: str = fields.PRICE_CATEGORY_LABEL
    else:
        label: pydantic_v1.constr(min_length=1, max_length=50) = fields.PRICE_CATEGORY_LABEL
    price: v1_serialization.offer_price_model = fields.PRICE
    id_at_provider: str | None = fields.ID_AT_PROVIDER_WITH_MAX_LENGTH

    class Config:
        getter_dict = DecimalPriceGetterDict


class EventOfferCreation(v1_serialization.OfferCreationBase):
    category_related_fields: v1_serialization.event_category_creation_fields
    event_duration: int | None = fields.EVENT_DURATION
    location: (
        v1_serialization.PhysicalLocation | v1_serialization.DigitalLocation | v1_serialization.AddressLocation
    ) = fields.OFFER_LOCATION
    has_ticket: bool = fields.EVENT_HAS_TICKET
    price_categories: list[PriceCategoryCreation] | None = fields.PRICE_CATEGORIES_WITH_MAX_ITEMS
    publication_date: datetime.datetime | None = fields.DEPRECATED_OFFER_PUBLICATION_DATE
    enable_double_bookings: bool | None = fields.OFFER_ENABLE_DOUBLE_BOOKINGS_ENABLED

    @pydantic_v1.root_validator(pre=True)
    def check_publication_date_and_publication_datetime_are_not_both_set(cls, values: dict) -> dict:
        publication_date = values.get("publicationDate")
        publication_datetime = values.get("publicationDatetime")

        if publication_date and publication_datetime:
            raise ValueError(
                "You cannot set both `publicationDate` and `publicationDatetime`. `publicationDate` is deprecated, please only use `publicationDatetime`."
            )

        return values

    @pydantic_v1.validator("price_categories")
    def get_unique_price_categories(
        cls,
        price_categories: list[PriceCategoryCreation],
    ) -> list[PriceCategoryCreation]:
        unique_price_categories = []
        unique_id_at_provider_list = set()
        for price_category in price_categories:
            # unique (label, price)
            if (price_category.label, price_category.price) in unique_price_categories:
                raise ValueError("Price categories must be unique")
            unique_price_categories.append((price_category.label, price_category.price))

            # unique idAtProvider
            if price_category.id_at_provider:
                if price_category.id_at_provider in unique_id_at_provider_list:
                    raise ValueError(
                        f"Price category `idAtProvider` must be unique. Duplicated value : {price_category.id_at_provider}"
                    )
                unique_id_at_provider_list.add(price_category.id_at_provider)

        return price_categories


class EventOfferEdition(v1_serialization.OfferEditionBase):
    category_related_fields: v1_serialization.event_category_edition_fields | None = (
        fields.EVENT_CATEGORIES_RELATED_FIELDS
    )
    event_duration: int | None = fields.EVENT_DURATION


class EventStockEdition(v1_serialization.BaseStockEdition):
    beginning_datetime: datetime.datetime | None = fields.BEGINNING_DATETIME
    price_category_id: pydantic_v1.PositiveInt | None = fields.PRICE_CATEGORY_ID
    id_at_provider: str | None = fields.ID_AT_PROVIDER_WITH_MAX_LENGTH

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")


class EventStockCreation(v1_serialization.BaseStockCreation):
    beginning_datetime: datetime.datetime = fields.BEGINNING_DATETIME
    booking_limit_datetime: datetime.datetime = fields.BOOKING_LIMIT_DATETIME
    price_category_id: int = fields.PRICE_CATEGORY_ID
    id_at_provider: str | None = fields.ID_AT_PROVIDER_WITH_MAX_LENGTH

    _validate_beginning_datetime = serialization_utils.validate_datetime("beginning_datetime")
    _validate_booking_limit_datetime = serialization_utils.validate_datetime("booking_limit_datetime")


class EventStocksCreation(serialization.ConfiguredBaseModel):
    dates: list[EventStockCreation] = fields.EVENT_STOCKS

    class Config:
        extra = "forbid"


class PriceCategoryResponse(serialization.ConfiguredBaseModel):
    id: int
    label: str = fields.PRICE_CATEGORY_LABEL
    price: pydantic_v1.StrictInt = fields.PRICE
    id_at_provider: str | None = fields.ID_AT_PROVIDER

    class Config:
        getter_dict = DecimalPriceGetterDict


class PriceCategoriesResponse(serialization.ConfiguredBaseModel):
    price_categories: list[PriceCategoryResponse] = fields.PRICE_CATEGORIES

    @classmethod
    def build_price_categories(cls, price_categories: list[offers_models.PriceCategory]) -> "PriceCategoriesResponse":
        return cls(price_categories=[PriceCategoryResponse.from_orm(category) for category in price_categories])


class EventOfferResponse(v1_serialization.OfferResponse, PriceCategoriesResponse):
    category_related_fields: v1_serialization.event_category_reading_fields
    event_duration: int | None = fields.EVENT_DURATION
    has_ticket: bool = fields.EVENT_HAS_TICKET
    publication_datetime: datetime.datetime | None = fields.OFFER_PUBLICATION_DATETIME

    @classmethod
    def build_event_offer(cls, offer: offers_models.Offer) -> "EventOfferResponse":
        base_offer_response = v1_serialization.OfferResponse.build_offer(offer)
        return cls(
            category_related_fields=v1_serialization.serialize_extra_data(offer),
            event_duration=offer.durationMinutes,
            has_ticket=offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP,
            price_categories=[
                PriceCategoryResponse.from_orm(price_category) for price_category in offer.priceCategories
            ],
            **base_offer_response.dict(),
        )


class EventOffersResponse(serialization.ConfiguredBaseModel):
    events: list[EventOfferResponse]


def _validate_ids_at_provider(cls: typing.Any, ids_at_provider: str) -> list[str] | None:
    if ids_at_provider:
        ids_at_provider_list = ids_at_provider.split(",")
        if len(ids_at_provider_list) > 100:
            raise ValueError("Too many ids")
        return ids_at_provider_list

    return None


class IsAtProviderQueryParams(base_serialization.IndexPaginationQueryParams):
    ids_at_provider: str | None = fields.IDS_AT_PROVIDER_FILTER

    _validate_ids_at_provider = pydantic_v1.validator("ids_at_provider", allow_reuse=True)(_validate_ids_at_provider)


class DateResponse(v1_serialization.BaseStockResponse):
    id: int
    beginning_datetime: datetime.datetime = fields.BEGINNING_DATETIME
    booking_limit_datetime: datetime.datetime = fields.BOOKING_LIMIT_DATETIME
    price_category: PriceCategoryResponse
    id_at_provider: str | None = fields.ID_AT_PROVIDER_WITH_MAX_LENGTH

    @classmethod
    def build_date(cls, stock: offers_models.Stock) -> "DateResponse":
        stock_response = v1_serialization.BaseStockResponse.build_stock(stock)
        return cls(
            id=stock.id,
            beginning_datetime=stock.beginningDatetime,  # type: ignore[arg-type]
            price_category=PriceCategoryResponse.from_orm(stock.priceCategory),
            id_at_provider=stock.idAtProviders,
            **stock_response.dict(),
        )


class PostDatesResponse(serialization.ConfiguredBaseModel):
    dates: list[DateResponse] = pydantic_v1.Field(description="Dates of the event.")


class GetDatesResponse(serialization.ConfiguredBaseModel):
    dates: list[DateResponse]


class PriceCategoriesCreation(serialization.ConfiguredBaseModel):
    price_categories: list[PriceCategoryCreation] = fields.PRICE_CATEGORIES_WITH_MAX_ITEMS

    @pydantic_v1.validator("price_categories")
    def get_unique_price_categories(
        cls,
        price_categories: list[PriceCategoryCreation],
    ) -> list[PriceCategoryCreation]:
        unique_price_categories = []
        unique_id_at_provider_list = set()
        for price_category in price_categories:
            # unique (label, price)
            if (price_category.label, price_category.price) in unique_price_categories:
                raise ValueError("Price categories must be unique")
            unique_price_categories.append((price_category.label, price_category.price))

            # unique idAtProvider
            if price_category.id_at_provider:
                if price_category.id_at_provider in unique_id_at_provider_list:
                    raise ValueError(
                        f"Price category `idAtProvider` must be unique. Duplicated value : {price_category.id_at_provider}"
                    )
                unique_id_at_provider_list.add(price_category.id_at_provider)

        return price_categories

    class Config:
        extra = "forbid"


class PriceCategoryEdition(serialization.ConfiguredBaseModel):
    if typing.TYPE_CHECKING:
        label: str = fields.PRICE_CATEGORY_LABEL
    else:
        label: pydantic_v1.constr(min_length=1, max_length=50) | None = fields.PRICE_CATEGORY_LABEL
    price: v1_serialization.offer_price_model | None = fields.PRICE
    id_at_provider: str | None = fields.ID_AT_PROVIDER_WITH_MAX_LENGTH

    @pydantic_v1.validator("price")
    def price_must_be_positive(cls, value: int | None) -> int | None:
        if value and value < 0:
            raise ValueError("Value must be positive")
        return value

    class Config:
        extra = "forbid"


class EventCategoryResponse(serialization.ConfiguredBaseModel):
    id: EventCategoryEnum  # type: ignore[valid-type]
    conditional_fields: dict[str, bool] = fields.EVENT_CONDITIONAL_FIELDS

    @classmethod
    def build_category(cls, subcategory: subcategories.Subcategory) -> "EventCategoryResponse":
        return cls(
            id=subcategory.id,
            conditional_fields={
                field: condition.is_required_in_external_form
                for field, condition in subcategory.conditional_fields.items()
            },
        )


class GetEventCategoriesResponse(serialization.ConfiguredBaseModel):
    __root__: list[EventCategoryResponse]
