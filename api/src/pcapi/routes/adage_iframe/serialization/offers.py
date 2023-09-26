from datetime import date
from datetime import datetime
import enum
import logging
import typing

from pydantic.v1 import Field
from pydantic.v1.class_validators import validator

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.native.v1.serialization import common_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.national_programs import NationalProgramModel
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
    def from_orm(cls, venue: offerers_models.Venue) -> "OfferVenueResponse":
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        result = super().from_orm(venue)
        return result

    id: int
    address: str | None
    city: str | None
    name: str
    postalCode: str | None
    publicName: str | None
    coordinates: common_models.Coordinates
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
    venueId: int | None
    name: str | None
    publicName: str | None
    address: str | None
    postalCode: str | None
    city: str | None

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


class EducationalRedactorResponseModel(BaseModel):
    email: str | None
    firstName: str | None
    lastName: str | None
    civility: str | None

    class Config:
        orm_mode = True


class CollectiveOfferResponseModel(BaseModel, common_models.AccessibilityComplianceMixin):
    id: int
    subcategoryLabel: str
    description: str | None
    isExpired: bool
    isSoldOut: bool
    name: str
    collectiveStock: OfferStockResponse = Field(alias="stock")
    venue: OfferVenueResponse
    students: list[educational_models.StudentLevels]
    offerVenue: CollectiveOfferOfferVenue
    contactEmail: str
    contactPhone: str | None
    durationMinutes: int | None
    offerId: int | None
    educationalPriceDetail: str | None
    domains: typing.Sequence[OfferDomain]
    institution: EducationalInstitutionResponseModel | None = Field(alias="educationalInstitution")
    interventionArea: list[str]
    imageCredit: str | None
    imageUrl: str | None
    teacher: EducationalRedactorResponseModel | None
    nationalProgram: NationalProgramModel | None
    isFavorite: bool | None

    @classmethod
    def build(
        cls,
        offer: educational_models.CollectiveOffer,
        is_favorite: bool,
        offerVenue: offerers_models.Venue | None = None,
    ) -> "CollectiveOfferResponseModel":
        return cls(
            id=offer.id,
            subcategoryLabel=offer.subcategory.app_label,
            description=offer.description,
            isExpired=offer.hasBookingLimitDatetimesPassed,  # type: ignore[arg-type]
            isSoldOut=offer.collectiveStock.isSoldOut,
            name=offer.name,
            collectiveStock=offer.collectiveStock,  # type: ignore[call-arg]
            venue=offer.venue,
            students=offer.students,
            offerVenue=CollectiveOfferOfferVenue(
                name=offerVenue.name if offerVenue else None,
                publicName=offerVenue.publicName if offerVenue else None,
                address=offerVenue.address if offerVenue else None,
                postalCode=offerVenue.postalCode if offerVenue else None,
                city=offerVenue.city if offerVenue else None,
                **offer.offerVenue,
            ),
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            durationMinutes=offer.durationMinutes,
            offerId=offer.offerId,
            educationalPriceDetail=offer.collectiveStock.priceDetail,
            domains=offer.domains,
            institution=offer.institution,
            interventionArea=offer.interventionArea,
            imageCredit=offer.imageCredit,
            imageUrl=offer.imageUrl,
            teacher=offer.teacher,
            nationalProgram=offer.nationalProgram,
            isFavorite=is_favorite,
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
        )

    class Config:
        alias_generator = to_camel
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True
        extra = "forbid"


class CollectiveOfferTemplateResponseModel(BaseModel, common_models.AccessibilityComplianceMixin):
    id: int
    subcategoryLabel: str
    description: str | None
    isExpired: bool
    isSoldOut: bool
    name: str
    venue: OfferVenueResponse
    students: list[educational_models.StudentLevels]
    offerVenue: CollectiveOfferOfferVenue
    contactEmail: str
    contactPhone: str | None
    durationMinutes: int | None
    educationalPriceDetail: str | None
    offerId: int | None
    domains: typing.Sequence[OfferDomain]
    interventionArea: list[str]
    imageCredit: str | None
    imageUrl: str | None
    nationalProgram: NationalProgramModel | None
    isFavorite: bool | None

    @classmethod
    def build(
        cls,
        offer: educational_models.CollectiveOfferTemplate,
        is_favorite: bool,
        offerVenue: offerers_models.Venue | None = None,
    ) -> "CollectiveOfferTemplateResponseModel":
        return cls(
            id=offer.id,
            subcategoryLabel=offer.subcategory.app_label,
            description=offer.description,
            isExpired=offer.hasBookingLimitDatetimesPassed,  # type: ignore[arg-type]
            isSoldOut=False,
            name=offer.name,
            venue=offer.venue,
            students=offer.students,
            offerVenue=CollectiveOfferOfferVenue(
                name=offerVenue.name if offerVenue else None,
                publicName=offerVenue.publicName if offerVenue else None,
                address=offerVenue.address if offerVenue else None,
                postalCode=offerVenue.postalCode if offerVenue else None,
                city=offerVenue.city if offerVenue else None,
                **offer.offerVenue,
            ),
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            durationMinutes=offer.durationMinutes,
            offerId=offer.offerId,
            educationalPriceDetail=offer.priceDetail,
            domains=offer.domains,
            interventionArea=offer.interventionArea,
            imageCredit=offer.imageCredit,
            imageUrl=offer.imageUrl,
            nationalProgram=offer.nationalProgram,
            isFavorite=is_favorite,
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
        )

    class Config:
        alias_generator = to_camel
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class CollectiveRequestResponseModel(BaseModel):
    id: int
    email: str
    phone_number: str | None
    requested_date: date | None
    total_students: int | None
    total_teachers: int | None
    comment: str

    class Config:
        alias_generator = to_camel
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class PostCollectiveRequestBodyModel(BaseModel):
    phone_number: str | None
    requested_date: date | None
    total_students: int | None
    total_teachers: int | None
    comment: str

    class Config:
        alias_generator = to_camel
