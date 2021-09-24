from datetime import datetime
import logging
from typing import Any
from typing import Callable
from typing import Optional

from pydantic.class_validators import validator
from pydantic.fields import Field

from pcapi.core.bookings.api import compute_cancellation_limit_date
from pcapi.core.categories import subcategories
from pcapi.core.categories.categories import CategoryIdEnum
from pcapi.core.categories.subcategories import HomepageLabelNameEnum
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.offers.models import ReasonMeta
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import ExpenseDomain
from pcapi.domain.music_types import MUSIC_SUB_TYPES_DICT
from pcapi.domain.music_types import MUSIC_TYPES_DICT
from pcapi.domain.show_types import SHOW_SUB_TYPES_DICT
from pcapi.domain.show_types import SHOW_TYPES_DICT
from pcapi.models.offer_type import CategoryNameEnum
from pcapi.models.offer_type import CategoryType
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date

from . import BaseModel


logger = logging.getLogger(__name__)


class OfferCategoryResponse(BaseModel):
    categoryType: CategoryType
    label: str
    name: Optional[CategoryNameEnum]


class OfferOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OfferStockActivationCodeResponse(BaseModel):
    expirationDate: Optional[datetime]


class OfferStockResponse(BaseModel):
    id: int
    beginningDatetime: Optional[datetime]
    bookingLimitDatetime: Optional[datetime]
    cancellation_limit_datetime: Optional[datetime]
    isBookable: bool
    isSoldOut: bool
    isExpired: bool
    price: int
    activationCode: Optional[OfferStockActivationCodeResponse]

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True

    @staticmethod
    def _get_cancellation_limit_datetime(stock: Stock) -> Optional[datetime]:
        # compute date as if it were booked now
        return compute_cancellation_limit_date(stock.beginningDatetime, datetime.now())

    @staticmethod
    def _get_non_scrappable_activation_code(stock: Stock) -> Optional[dict]:
        if not stock.canHaveActivationCodes:
            return None
        # here we have N+1 requests (for each stock we query an activation code)
        # but it should be more efficient than loading all activationCodes of all stocks
        activation_code = offers_repository.get_available_activation_code(stock)
        if not activation_code:
            return None
        return {"expirationDate": activation_code.expirationDate}

    @classmethod
    def from_orm(cls, stock):  # type: ignore
        stock.cancellation_limit_datetime = cls._get_cancellation_limit_datetime(stock)
        stock.activationCode = cls._get_non_scrappable_activation_code(stock)
        return super().from_orm(stock)


class OfferVenueResponse(BaseModel):
    @classmethod
    def from_orm(cls, venue):  # type: ignore
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        return super().from_orm(venue)

    id: int
    address: Optional[str]
    city: Optional[str]
    managingOfferer: OfferOffererResponse = Field(..., alias="offerer")
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]
    coordinates: Coordinates

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


LABELS_BY_DICT_MAPPING = {"musicSubType": ""}


def get_id_converter(labels_by_id: dict, field_name: str) -> Callable[[Optional[str]], Optional[str]]:
    def convert_id_into_label(value_id: Optional[str]) -> Optional[str]:
        try:
            return labels_by_id[int(value_id)] if value_id else None
        except ValueError:  # on the second time this function is called twice, the field is already converted
            return None
        except KeyError:
            logger.exception("Invalid '%s' '%s' found on an offer", field_name, value_id)
            return None

    return convert_id_into_label


class OfferExtraData(BaseModel):
    author: Optional[str]
    durationMinutes: Optional[int]
    isbn: Optional[str]
    musicSubType: Optional[str]
    musicType: Optional[str]
    performer: Optional[str]
    showSubType: Optional[str]
    showType: Optional[str]
    stageDirector: Optional[str]
    speaker: Optional[str]
    visa: Optional[str]

    _convert_music_sub_type = validator("musicSubType", pre=True, allow_reuse=True)(
        get_id_converter(MUSIC_SUB_TYPES_DICT, "musicSubType")
    )
    _convert_music_type = validator("musicType", pre=True, allow_reuse=True)(
        get_id_converter(MUSIC_TYPES_DICT, "musicType")
    )
    _convert_show_sub_type = validator("showSubType", pre=True, allow_reuse=True)(
        get_id_converter(SHOW_SUB_TYPES_DICT, "showSubType")
    )
    _convert_show_type = validator("showType", pre=True, allow_reuse=True)(
        get_id_converter(SHOW_TYPES_DICT, "showType")
    )


class OfferAccessibilityResponse(BaseModel):
    audioDisability: Optional[bool]
    mentalDisability: Optional[bool]
    motorDisability: Optional[bool]
    visualDisability: Optional[bool]


class OfferImageResponse(BaseModel):
    url: str
    credit: Optional[str]

    class Config:
        orm_mode = True


def get_serialized_offer_category(offer: Offer) -> dict:
    return {
        "name": offer.offer_category_name_for_app,
        "label": offer.offerType["appLabel"],
        "categoryType": offer.category_type,
    }


class OfferResponse(BaseModel):
    @classmethod
    def from_orm(cls: Any, offer: Offer):  # type: ignore
        offer.category = get_serialized_offer_category(offer)
        offer.accessibility = {
            "audioDisability": offer.audioDisabilityCompliant,
            "mentalDisability": offer.mentalDisabilityCompliant,
            "motorDisability": offer.motorDisabilityCompliant,
            "visualDisability": offer.visualDisabilityCompliant,
        }
        offer.expense_domains = get_expense_domains(offer)
        offer.isExpired = offer.hasBookingLimitDatetimesPassed

        result = super().from_orm(offer)

        if result.extraData:
            result.extraData.durationMinutes = offer.durationMinutes
        else:
            result.extraData = OfferExtraData(durationMinutes=offer.durationMinutes)

        return result

    id: int
    accessibility: OfferAccessibilityResponse
    description: Optional[str]
    expense_domains: list[ExpenseDomain]
    externalTicketOfficeUrl: Optional[str]
    extraData: Optional[OfferExtraData]
    isExpired: bool
    isReleased: bool
    isSoldOut: bool
    isDigital: bool
    isDuo: bool
    isEducational: bool
    name: str
    category: OfferCategoryResponse
    subcategoryId: SubcategoryIdEnum
    stocks: list[OfferStockResponse]
    image: Optional[OfferImageResponse]
    venue: OfferVenueResponse
    withdrawalDetails: Optional[str]

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}


class OfferReportRequest(BaseModel):
    class Config:
        alias_generator = to_camel

    reason: str
    custom_reason: Optional[str]

    @validator("custom_reason")
    def custom_reason_must_not_be_too_long(  # pylint: disable=no-self-argument
        cls, content: Optional[str]
    ) -> Optional[str]:
        if not content:
            return None

        if len(content) > 512:
            raise ValueError("custom reason is too long")

        return content

    @validator("reason")
    def reason_is_valid_enum_value(cls, reason: str) -> str:  # pylint: disable=no-self-argument
        if reason not in {r.value for r in Reason}:
            raise ValueError("unknown reason")
        return reason


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
    id: SubcategoryIdEnum
    category_id: CategoryIdEnum
    app_label: str
    search_group_name: Optional[subcategories.SearchGroupNameEnum]
    homepage_label_name: HomepageLabelNameEnum
    is_event: bool
    online_offline_platform: subcategories.OnlineOfflinePlatformChoicesEnum

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class SearchGroupResponseModel(BaseModel):
    name: str
    value: Optional[str]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class HomepageLabelResponseModel(BaseModel):
    name: str
    value: Optional[str]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class SubcategoriesResponseModel(BaseModel):
    subcategories: list[SubcategoryResponseModel]
    searchGroups: list[SearchGroupResponseModel]
    homepageLabels: list[HomepageLabelResponseModel]
