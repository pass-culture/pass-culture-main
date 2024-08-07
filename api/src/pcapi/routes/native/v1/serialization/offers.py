from datetime import date
from datetime import datetime
import logging
from typing import Any
from typing import Callable
from typing import TypeVar

from pydantic.v1.class_validators import validator
from pydantic.v1.fields import Field
from pydantic.v1.utils import GetterDict

from pcapi.core.bookings.api import compute_booking_cancellation_limit_date
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import offer_metadata
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.offers.models import ReasonMeta
from pcapi.core.providers import constants as provider_constants
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.users.models import ExpenseDomain
from pcapi.domain.movie_types import get_movie_label
from pcapi.domain.music_types import MUSIC_SUB_TYPES_LABEL_BY_CODE
from pcapi.domain.music_types import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.domain.show_types import SHOW_SUB_TYPES_LABEL_BY_CODE
from pcapi.domain.show_types import SHOW_TYPES_LABEL_BY_CODE
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class OfferOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OfferStockActivationCodeResponse(BaseModel):
    expirationDate: datetime | None


class OfferStockResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        stock = self._obj
        if key == "cancellation_limit_datetime":
            return compute_booking_cancellation_limit_date(stock.beginningDatetime, datetime.utcnow())

        if key == "activationCode":
            if not stock.canHaveActivationCodes:
                return None
            # here we have N+1 requests (for each stock we query an activation code)
            # but it should be more efficient than loading all activationCodes of all stocks
            activation_code = offers_repository.get_available_activation_code(stock)
            if not activation_code:
                return None
            return {"expirationDate": activation_code.expirationDate}

        if key == "priceCategoryLabel":
            if price_category := stock.priceCategory:
                return price_category.priceCategoryLabel.label
            return None

        return super().get(key, default)


class OfferStockResponse(ConfiguredBaseModel):
    id: int
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    cancellation_limit_datetime: datetime | None
    features: list[str]
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
        getter_dict = OfferStockResponseGetterDict


class OfferVenueResponse(BaseModel):
    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "OfferVenueResponse":
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        venue.address = venue.street
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
    timezone: str
    bannerUrl: str | None

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


class GtlLabels(BaseModel):
    label: str
    level01Label: str | None
    level02Label: str | None
    level03Label: str | None
    level04Label: str | None


class OfferExtraData(BaseModel):
    allocineId: int | None
    author: str | None
    durationMinutes: int | None
    ean: str | None
    musicSubType: str | None
    musicType: str | None
    performer: str | None
    showSubType: str | None
    showType: str | None
    stageDirector: str | None
    speaker: str | None
    visa: str | None
    releaseDate: date | None
    cast: list[str] | None
    editeur: str | None
    gtlLabels: GtlLabels | None
    genres: list[str] | None

    @validator("genres", pre=True, allow_reuse=True)
    def convert_movie_types(cls, genres: list[str] | None) -> list[str] | None:
        if not genres:
            return None
        movie_types = []
        for genre in genres:
            movie_type = get_movie_label(genre)
            if movie_type:
                movie_types.append(movie_type)
        return movie_types

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


def get_gtl_labels(gtl_id: str) -> GtlLabels | None:
    if gtl_id not in GTLS:
        return None
    gtl_infos = GTLS[gtl_id]
    label = gtl_infos.get("label")
    if label:
        return GtlLabels(
            label=label,
            level01Label=gtl_infos.get("level_01_label"),
            level02Label=gtl_infos.get("level_02_label"),
            level03Label=gtl_infos.get("level_03_label"),
            level04Label=gtl_infos.get("level_04_label"),
        )
    logger.error("GTL label not found for id %s", gtl_id)
    return None


BaseOfferResponseType = TypeVar("BaseOfferResponseType", bound="BaseOfferResponse")


class ReactionCount(BaseModel):
    likes: int


class BaseOfferResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        offer = self._obj
        product = offer.product
        if key == "reactions_count":
            if product:
                likes = sum(1 for reaction in product.reactions if reaction.reactionType == ReactionTypeEnum.LIKE)
            else:
                likes = sum(1 for reaction in offer.reactions if reaction.reactionType == ReactionTypeEnum.LIKE)
            return ReactionCount(likes=likes)

        if key == "accessibility":
            return {
                "audioDisability": offer.audioDisabilityCompliant,
                "mentalDisability": offer.mentalDisabilityCompliant,
                "motorDisability": offer.motorDisabilityCompliant,
                "visualDisability": offer.visualDisabilityCompliant,
            }

        if key == "expense_domains":
            return get_expense_domains(offer)

        if key == "isExpired":
            return offer.hasBookingLimitDatetimesPassed

        if key == "metadata":
            return offer_metadata.get_metadata_from_offer(offer)

        if key == "isExternalBookingsDisabled":
            if offer.lastProvider and offer.lastProvider.localClass in provider_constants.PROVIDER_LOCAL_CLASS_TO_FF:
                return provider_constants.PROVIDER_LOCAL_CLASS_TO_FF[offer.lastProvider.localClass].is_active()

            return False

        if key == "last30DaysBookings":
            return offer.product.last_30_days_booking if offer.product else None

        if key == "stocks":
            return [OfferStockResponse.from_orm(stock) for stock in offer.activeStocks]

        if key == "extraData":
            if not offer.extraData:
                extraData = OfferExtraData()  # type: ignore[call-arg]
            else:
                extraData = OfferExtraData.parse_obj(offer.extraData)

            # insert the durationMinutes in the extraData
            extraData.durationMinutes = offer.durationMinutes

            # insert the GLT labels in the extraData
            gtl_id = offer.extraData.get("gtl_id") if offer.extraData else None
            if gtl_id is not None:
                extraData.gtlLabels = get_gtl_labels(gtl_id)

            return extraData

        return super().get(key, default)


class BaseOfferResponse(ConfiguredBaseModel):
    id: int
    accessibility: OfferAccessibilityResponse
    description: str | None
    expense_domains: list[ExpenseDomain]
    externalTicketOfficeUrl: str | None
    extraData: OfferExtraData | None
    isExpired: bool
    isExternalBookingsDisabled: bool
    is_forbidden_to_underage: bool
    isReleased: bool
    isSoldOut: bool
    isDigital: bool
    isDuo: bool
    isEducational: bool
    last30DaysBookings: int | None
    metadata: offer_metadata.Metadata
    name: str
    reactions_count: ReactionCount
    stocks: list[OfferStockResponse]
    subcategoryId: subcategories.SubcategoryIdEnum
    venue: OfferVenueResponse
    withdrawalDetails: str | None

    class Config:
        getter_dict = BaseOfferResponseGetterDict


class OfferResponse(BaseOfferResponse):
    image: OfferImageResponse | None


class OfferResponseV2(BaseOfferResponse):
    images: dict[str, OfferImageResponse] | None


class OfferPreviewResponse(BaseModel):
    @classmethod
    def from_orm(cls, offer: Offer) -> "OfferPreviewResponse":
        offer_preview = super().from_orm(offer)
        offer_preview.stocks = [OfferStockResponse.from_orm(stock) for stock in offer.activeStocks]

        return offer_preview

    id: int
    durationMinutes: int | None
    extraData: OfferExtraData | None
    image: OfferImageResponse | None
    last30DaysBookings: int | None
    name: str
    stocks: list[OfferStockResponse]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class OffersStocksResponse(BaseModel):
    offers: list[OfferPreviewResponse]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class OffersStocksResponseV2(BaseModel):
    offers: list[OfferResponseV2]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class OffersStocksRequest(BaseModel):
    offer_ids: list[int]


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
