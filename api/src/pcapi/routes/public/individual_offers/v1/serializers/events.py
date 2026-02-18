import datetime
import decimal
import typing

import pydantic as pydantic_v2
import pydantic.v1 as pydantic_v1
from pydantic.v1.utils import GetterDict

from pcapi.core.categories import subcategories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import models as offers_models
from pcapi.core.videos import api as videos_api
from pcapi.core.videos import exceptions as videos_exceptions
from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.documentation_constants.fields_v2 import fields_v2
from pcapi.routes.public.individual_offers.v1 import base_serialization
from pcapi.routes.public.individual_offers.v1 import serialization as v1_serialization
from pcapi.routes.public.serialization.utils import StrEnum
from pcapi.serialization import utils as serialization_utils


class EventCategoryEnum(StrEnum):
    ACTIVATION_EVENT = "ACTIVATION_EVENT"
    ATELIER_PRATIQUE_ART = "ATELIER_PRATIQUE_ART"
    CINE_PLEIN_AIR = "CINE_PLEIN_AIR"
    CONCERT = "CONCERT"
    CONCOURS = "CONCOURS"
    CONFERENCE = "CONFERENCE"
    DECOUVERTE_METIERS = "DECOUVERTE_METIERS"
    EVENEMENT_CINE = "EVENEMENT_CINE"
    EVENEMENT_JEU = "EVENEMENT_JEU"
    EVENEMENT_MUSIQUE = "EVENEMENT_MUSIQUE"
    EVENEMENT_PATRIMOINE = "EVENEMENT_PATRIMOINE"
    FESTIVAL_ART_VISUEL = "FESTIVAL_ART_VISUEL"
    FESTIVAL_CINE = "FESTIVAL_CINE"
    FESTIVAL_LIVRE = "FESTIVAL_LIVRE"
    FESTIVAL_MUSIQUE = "FESTIVAL_MUSIQUE"
    FESTIVAL_SPECTACLE = "FESTIVAL_SPECTACLE"
    LIVESTREAM_EVENEMENT = "LIVESTREAM_EVENEMENT"
    LIVESTREAM_MUSIQUE = "LIVESTREAM_MUSIQUE"
    LIVESTREAM_PRATIQUE_ARTISTIQUE = "LIVESTREAM_PRATIQUE_ARTISTIQUE"
    RENCONTRE_EN_LIGNE = "RENCONTRE_EN_LIGNE"
    RENCONTRE_JEU = "RENCONTRE_JEU"
    RENCONTRE = "RENCONTRE"
    SALON = "SALON"
    SEANCE_CINE = "SEANCE_CINE"
    SEANCE_ESSAI_PRATIQUE_ART = "SEANCE_ESSAI_PRATIQUE_ART"
    SPECTACLE_REPRESENTATION = "SPECTACLE_REPRESENTATION"
    VISITE_GUIDEE = "VISITE_GUIDEE"
    VISITE = "VISITE"


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


def _validate_category_related_fields(
    category_related_fields: v1_serialization.event_category_reading_fields | None,
) -> v1_serialization.event_category_reading_fields | None:
    """Validate music fields until some more checks are needed.

    Note: this is perhaps not the best place to run these
    validations. Maybe the models definition should be updated to
    set the real and expected category-dependant combinations. But
    for now, lets run some checks this way.
    """
    if not category_related_fields:
        return None

    # only MUSIC_TYPE should be needed but since the
    # category_related_fields is built using some black magic, lets
    # be safe and use the two existing music-related enum values.
    music_field_names = {
        subcategories.ExtraDataFieldEnum.MUSIC_TYPE.value,
        subcategories.ExtraDataFieldEnum.MUSIC_SUB_TYPE.value,
    }

    for field_name, field_value in category_related_fields.dict(exclude_unset=True).items():
        if field_name in music_field_names and field_value is None:
            raise ValueError("If musicType is set, it cannot be NULL")

    return category_related_fields


def validate_category_related_fields(field_name: str, always: bool = False) -> classmethod:
    return pydantic_v1.validator(field_name, pre=False, allow_reuse=True, always=always)(
        _validate_category_related_fields
    )


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
    video_url: pydantic_v1.HttpUrl | None = fields.VIDEO_URL

    _validate_category_related_fields = validate_category_related_fields("category_related_fields")

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

    @pydantic_v1.validator("video_url")
    def check_video_is_from_youtube(
        cls,
        video_url: pydantic_v1.HttpUrl | None,
    ) -> pydantic_v1.HttpUrl | None:
        if video_url:
            try:
                videos_api.extract_video_id(video_url)
            except videos_exceptions.InvalidVideoUrl:
                raise ValueError(
                    "Your video must be from the Youtube plateform, it should be public and should not be a short nor a user's profile"
                )
        return video_url


class EventOfferEdition(v1_serialization.OfferEditionBase):
    category_related_fields: v1_serialization.event_category_edition_fields | None = (
        fields.EVENT_CATEGORIES_RELATED_FIELDS
    )
    event_duration: int | None = fields.EVENT_DURATION
    video_url: pydantic_v1.HttpUrl | None = fields.VIDEO_URL

    _validate_category_related_fields = validate_category_related_fields("category_related_fields")

    @pydantic_v1.validator("video_url")
    def check_video_is_from_youtube(
        cls,
        video_url: pydantic_v1.HttpUrl | None,
    ) -> pydantic_v1.HttpUrl | None:
        if video_url:
            try:
                videos_api.extract_video_id(video_url)
            except videos_exceptions.InvalidVideoUrl:
                raise ValueError(
                    "Your video must be from the Youtube plateform, it should be public and should not be a short nor a user's profile"
                )
        return video_url


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
    video_url: pydantic_v1.HttpUrl | None = fields.VIDEO_URL

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
            video_url=typing.cast(pydantic_v1.HttpUrl, offer.metaData.videoUrl) if offer.metaData else None,
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


class EventCategoryResponse(serialization.HttpBodyModel):
    id: EventCategoryEnum = fields_v2.EVENT_CATEGORY_ID
    conditional_fields: dict[str, bool] = fields_v2.EVENT_CONDITIONAL_FIELDS
    label: str = fields_v2.EVENT_CATEGORY_LABEL


class GetEventCategoriesResponse(pydantic_v2.RootModel):
    root: list[EventCategoryResponse]
