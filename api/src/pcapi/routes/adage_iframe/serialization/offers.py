from datetime import datetime
import enum
import logging
from typing import Any

from pydantic import Field
from pydantic.class_validators import validator

from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import StudentLevels
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceStrictMixin
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class OfferManagingOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OfferStockResponse(BaseModel):
    id: int
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    isBookable: bool
    price: int
    numberOfTickets: int | None
    educationalPriceDetail: str | None

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class OfferVenueResponse(BaseModel):
    @classmethod
    def from_orm(cls, venue):  # type: ignore
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        result = super().from_orm(venue)
        return result

    id: int
    address: str | None
    city: str | None
    name: str
    postalCode: str | None
    publicName: str | None
    coordinates: Coordinates
    managingOfferer: OfferManagingOffererResponse

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class CategoryResponseModel(BaseModel):
    id: str
    pro_label: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class SubcategoryResponseModel(BaseModel):
    id: str
    category_id: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class CategoriesResponseModel(BaseModel):
    categories: list[CategoryResponseModel]
    subcategories: list[SubcategoryResponseModel]

    class Config:
        orm_mode = True


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"


class CollectiveOfferOfferVenue(BaseModel):
    addressType: OfferAddressType
    otherAddress: str
    venueId: str

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferDomain(BaseModel):
    id: int
    name: str

    class Config:
        alias_generator = to_camel
        orm_mode = True


class EducationalInstitutionResponseModel(BaseModel):
    id: int
    name: str
    postalCode: str
    city: str
    institutionType: str | None

    class Config:
        orm_mode = True
        extra = "forbid"


class CollectiveOfferResponseModel(BaseModel, AccessibilityComplianceStrictMixin):
    id: int
    subcategoryLabel: str
    description: str | None
    isExpired: bool
    isSoldOut: bool
    name: str
    collectiveStock: OfferStockResponse = Field(alias="stock")
    venue: OfferVenueResponse
    students: list[StudentLevels]
    offerVenue: CollectiveOfferOfferVenue
    contactEmail: str
    contactPhone: str
    durationMinutes: int | None
    offerId: str | None
    educationalPriceDetail: str | None
    domains: list[OfferDomain]
    institution: EducationalInstitutionResponseModel | None = Field(alias="educationalInstitution")
    interventionArea: list[str]

    @classmethod
    def from_orm(cls: Any, offer: CollectiveOffer):  # type: ignore
        offer.subcategoryLabel = offer.subcategory.app_label
        offer.isExpired = offer.hasBookingLimitDatetimesPassed

        result = super().from_orm(offer)

        result.isSoldOut = offer.collectiveStock.isSoldOut
        result.educationalPriceDetail = offer.collectiveStock.priceDetail

        return result

    class Config:
        alias_generator = to_camel
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True
        extra = "forbid"


class CollectiveOfferTemplateResponseModel(BaseModel, AccessibilityComplianceStrictMixin):
    id: int
    subcategoryLabel: str
    description: str | None
    isExpired: bool
    isSoldOut: bool
    name: str
    venue: OfferVenueResponse
    students: list[StudentLevels]
    offerVenue: CollectiveOfferOfferVenue
    contactEmail: str
    contactPhone: str
    durationMinutes: int | None
    educationalPriceDetail: str | None
    offerId: str | None
    domains: list[OfferDomain]
    interventionArea: list[str]

    @classmethod
    def from_orm(cls: Any, offer: CollectiveOfferTemplate):  # type: ignore
        offer.subcategoryLabel = offer.subcategory.app_label
        offer.isExpired = offer.hasBookingLimitDatetimesPassed

        result = super().from_orm(offer)

        result.isSoldOut = False
        result.educationalPriceDetail = offer.priceDetail

        return result

    class Config:
        alias_generator = to_camel
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True
