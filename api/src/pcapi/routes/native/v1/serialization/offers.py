from datetime import datetime
import logging
from typing import Callable

from pydantic.class_validators import validator
from pydantic.fields import Field

from pcapi.core.bookings.api import compute_booking_cancellation_limit_date
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import offer_metadata
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.offers.models import ReasonMeta
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import ExpenseDomain
from pcapi.domain.music_types import MUSIC_SUB_TYPES_LABEL_BY_CODE
from pcapi.domain.music_types import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.domain.show_types import SHOW_SUB_TYPES_LABEL_BY_CODE
from pcapi.domain.show_types import SHOW_TYPES_LABEL_BY_CODE
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class OfferOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OfferStockActivationCodeResponse(BaseModel):
    expirationDate: datetime | None


class OfferStockResponse(BaseModel):
    id: int
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    cancellation_limit_datetime: datetime | None
    isBookable: bool
    is_forbidden_to_underage: bool
    isSoldOut: bool
    isExpired: bool
    price: int
    activationCode: OfferStockActivationCodeResponse | None
    priceCategoryLabel: str | None
    remainingQuantity: int | None

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_remainingQuantity = validator(
        "remainingQuantity",
        pre=True,
        allow_reuse=True,
    )(lambda quantity: quantity if quantity != "unlimited" else None)

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True

    @staticmethod
    def _get_cancellation_limit_datetime(stock: Stock) -> datetime | None:
        # compute date as if it were booked now
        return compute_booking_cancellation_limit_date(stock.beginningDatetime, datetime.utcnow())

    @staticmethod
    def _get_non_scrappable_activation_code(stock: Stock) -> dict | None:
        if not stock.canHaveActivationCodes:
            return None
        # here we have N+1 requests (for each stock we query an activation code)
        # but it should be more efficient than loading all activationCodes of all stocks
        activation_code = offers_repository.get_available_activation_code(stock)
        if not activation_code:
            return None
        return {"expirationDate": activation_code.expirationDate}

    @classmethod
    def from_orm(cls, stock: Stock) -> "OfferStockResponse":
        stock.cancellation_limit_datetime = cls._get_cancellation_limit_datetime(stock)
        stock.activationCode = cls._get_non_scrappable_activation_code(stock)
        stock_response = super().from_orm(stock)

        price_category = getattr(stock, "priceCategory", None)
        stock_response.priceCategoryLabel = price_category.priceCategoryLabel.label if price_category else None

        return stock_response


class OfferVenueResponse(BaseModel):
    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "OfferVenueResponse":
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        result = super().from_orm(venue)
        return result

    id: int
    address: str | None
    city: str | None
    managingOfferer: OfferOffererResponse = Field(..., alias="offerer")
    name: str
    postalCode: str | None
    publicName: str | None
    coordinates: Coordinates
    isPermanent: bool

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class OfferNearestVenuesParam(Coordinates):
    page: int = 1
    per_page: int = 10


class OfferNearestVenuesResponse(BaseModel):
    venues: list[OfferVenueResponse]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


def get_id_converter(labels_by_id: dict, field_name: str) -> Callable[[str | None], str | None]:
    def convert_id_into_label(value_id: str | None) -> str | None:
        try:
            return labels_by_id[int(value_id)] if value_id else None
        except ValueError:  # on the second time this function is called twice, the field is already converted
            return None
        except KeyError:
            logger.exception("Invalid '%s' '%s' found on an offer", field_name, value_id)
            return None

    return convert_id_into_label


class OfferExtraData(BaseModel):
    author: str | None
    durationMinutes: int | None
    isbn: str | None
    musicSubType: str | None
    musicType: str | None
    performer: str | None
    showSubType: str | None
    showType: str | None
    stageDirector: str | None
    speaker: str | None
    visa: str | None

    _convert_music_sub_type = validator("musicSubType", pre=True, allow_reuse=True)(
        get_id_converter(MUSIC_SUB_TYPES_LABEL_BY_CODE, "musicSubType")
    )
    _convert_music_type = validator("musicType", pre=True, allow_reuse=True)(
        get_id_converter(MUSIC_TYPES_LABEL_BY_CODE, "musicType")
    )
    _convert_show_sub_type = validator("showSubType", pre=True, allow_reuse=True)(
        get_id_converter(SHOW_SUB_TYPES_LABEL_BY_CODE, "showSubType")
    )
    _convert_show_type = validator("showType", pre=True, allow_reuse=True)(
        get_id_converter(SHOW_TYPES_LABEL_BY_CODE, "showType")
    )


class OfferAccessibilityResponse(BaseModel):
    audioDisability: bool | None
    mentalDisability: bool | None
    motorDisability: bool | None
    visualDisability: bool | None


class OfferImageResponse(BaseModel):
    url: str
    credit: str | None

    class Config:
        orm_mode = True


class OfferResponse(BaseModel):
    @classmethod
    def from_orm(cls, offer: Offer) -> "OfferResponse":
        offer.accessibility = {
            "audioDisability": offer.audioDisabilityCompliant,
            "mentalDisability": offer.mentalDisabilityCompliant,
            "motorDisability": offer.motorDisabilityCompliant,
            "visualDisability": offer.visualDisabilityCompliant,
        }
        offer.expense_domains = get_expense_domains(offer)
        offer.isExpired = offer.hasBookingLimitDatetimesPassed
        offer.metadata = offer_metadata.get_metadata_from_offer(offer)

        result = super().from_orm(offer)

        if result.extraData:
            result.extraData.durationMinutes = offer.durationMinutes
        else:
            result.extraData = OfferExtraData(durationMinutes=offer.durationMinutes)  # type: ignore [call-arg]

        return result

    id: int
    accessibility: OfferAccessibilityResponse
    description: str | None
    expense_domains: list[ExpenseDomain]
    externalTicketOfficeUrl: str | None
    extraData: OfferExtraData | None
    isExpired: bool
    is_forbidden_to_underage: bool
    isReleased: bool
    isSoldOut: bool
    isDigital: bool
    isDuo: bool
    isEducational: bool
    metadata: offer_metadata.Metadata
    name: str
    stocks: list[OfferStockResponse]
    subcategoryId: subcategories.SubcategoryIdEnum
    image: OfferImageResponse | None
    venue: OfferVenueResponse
    withdrawalDetails: str | None

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}


class OfferReportRequest(BaseModel):
    class Config:
        alias_generator = to_camel

    reason: Reason
    custom_reason: str | None

    @validator("custom_reason")
    def custom_reason_must_not_be_too_long(cls, content: str | None) -> str | None:
        if not content:
            return None

        if len(content) > 512:
            raise ValueError("custom reason is too long")

        return content


class OfferReportReasons(BaseModel):
    class Config:
        alias_generator = to_camel

    reasons: dict[str, ReasonMeta]


class ReportedOffer(BaseModel):
    offer_id: int
    reported_at: datetime
    reason: Reason

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class UserReportedOffersResponse(BaseModel):
    reported_offers: list[ReportedOffer]

    class Config:
        alias_generator = to_camel


class SubcategoryResponseModel(BaseModel):
    id: subcategories.SubcategoryIdEnum
    category_id: categories.CategoryIdEnum
    app_label: str
    search_group_name: subcategories.SearchGroupNameEnum
    homepage_label_name: subcategories.HomepageLabelNameEnum
    is_event: bool
    online_offline_platform: subcategories.OnlineOfflinePlatformChoicesEnum

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class SearchGroupResponseModel(BaseModel):
    name: subcategories.SearchGroupNameEnum
    value: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class HomepageLabelResponseModel(BaseModel):
    name: subcategories.HomepageLabelNameEnum
    value: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class SubcategoriesResponseModel(BaseModel):
    subcategories: list[SubcategoryResponseModel]
    searchGroups: list[SearchGroupResponseModel]
    homepageLabels: list[HomepageLabelResponseModel]
