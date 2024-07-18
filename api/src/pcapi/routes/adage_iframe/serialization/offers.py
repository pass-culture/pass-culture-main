from datetime import date
from datetime import datetime
from decimal import Decimal
import enum
import logging
import typing

from pydantic.v1 import Field
from pydantic.v1 import root_validator
from pydantic.v1.class_validators import validator

import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.categories.subcategories_v2 import EacFormat
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.native.v1.serialization import common_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.collective_offers_serialize import validate_venue_id
from pcapi.routes.serialization.national_programs import NationalProgramModel
from pcapi.routes.shared import validation
from pcapi.routes.shared.price import convert_to_cent
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pydantic import model_validator, ConfigDict


logger = logging.getLogger(__name__)


class OfferManagingOffererResponse(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class OfferStockResponse(BaseModel):
    id: int
    beginningDatetime: datetime | None
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    isBookable: bool
    price: int
    numberOfTickets: int | None
    educationalPriceDetail: str | None

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True, json_encoders={datetime: format_into_utc_date})


class OfferVenueResponse(BaseModel):
    id: int
    address: str | None
    city: str | None
    name: str
    postalCode: str | None
    departementCode: str | None = Field(alias="departmentCode")
    publicName: str | None
    coordinates: common_models.Coordinates
    managingOfferer: OfferManagingOffererResponse
    adageId: str | None
    distance: Decimal | None
    bannerUrl: str | None = Field(alias="imgUrl")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "OfferVenueResponse":
        venue.coordinates = {"latitude": venue.latitude, "longitude": venue.longitude}
        venue.address = venue.street
        result = super().from_orm(venue)
        return result


class CategoryResponseModel(BaseModel):
    id: str
    pro_label: str
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class SubcategoryResponseModel(BaseModel):
    id: str
    category_id: str
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CategoriesResponseModel(BaseModel):
    categories: list[CategoryResponseModel]
    subcategories: list[SubcategoryResponseModel]
    model_config = ConfigDict(from_attributes=True)


class EacFormatsResponseModel(BaseModel):
    formats: typing.Sequence[subcategories.EacFormat]
    model_config = ConfigDict(use_enum_values=True)


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
    distance: Decimal | None

    _validated_venue_id = validator("venueId", pre=True, allow_reuse=True)(validate_venue_id)
    model_config = ConfigDict(alias_generator=to_camel, extra="forbid")


class OfferDomain(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)


class EducationalInstitutionResponseModel(BaseModel):
    id: int
    name: str
    postalCode: str
    city: str
    institutionType: str | None
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class EducationalRedactorResponseModel(BaseModel):
    email: str | None
    firstName: str | None
    lastName: str | None
    civility: str | None
    model_config = ConfigDict(from_attributes=True)


class CollectiveOfferResponseModel(BaseModel, common_models.AccessibilityComplianceMixin):
    id: int
    description: str | None
    isExpired: bool
    isSoldOut: bool
    name: str
    collectiveStock: OfferStockResponse = Field(alias="stock")
    venue: OfferVenueResponse
    students: list[educational_models.StudentLevels]
    offerVenue: CollectiveOfferOfferVenue
    contactEmail: str | None
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
    formats: typing.Sequence[EacFormat] | None
    isTemplate: bool = False

    @classmethod
    def build(
        cls,
        offer: educational_models.CollectiveOffer,
        is_favorite: bool,
        offerVenue: offerers_models.Venue | None = None,
    ) -> "CollectiveOfferResponseModel":
        return cls(
            id=offer.id,
            description=offer.description,
            isExpired=offer.hasBookingLimitDatetimesPassed,
            isSoldOut=offer.collectiveStock.isSoldOut,
            name=offer.name,
            collectiveStock=offer.collectiveStock,  # type: ignore[call-arg]
            venue=offer.venue,
            students=offer.students,
            offerVenue=CollectiveOfferOfferVenue(
                name=offerVenue.name if offerVenue else None,
                publicName=offerVenue.publicName if offerVenue else None,
                address=offerVenue.street if offerVenue else None,
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
            formats=offer.get_formats(),
        )
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True, json_encoders={datetime: format_into_utc_date}, use_enum_values=True, extra="forbid")


class ListCollectiveOffersResponseModel(BaseModel):
    collectiveOffers: list[CollectiveOfferResponseModel]
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={datetime: format_into_utc_date})


class TemplateDatesModel(BaseModel):
    start: datetime
    end: datetime
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={datetime: format_into_utc_date})


class CollectiveOfferTemplateResponseModel(BaseModel, common_models.AccessibilityComplianceMixin):
    id: int
    description: str | None
    isExpired: bool
    isSoldOut: bool
    name: str
    venue: OfferVenueResponse
    students: list[educational_models.StudentLevels]
    offerVenue: CollectiveOfferOfferVenue
    durationMinutes: int | None
    educationalPriceDetail: str | None
    offerId: int | None
    domains: typing.Sequence[OfferDomain]
    interventionArea: list[str]
    imageCredit: str | None
    imageUrl: str | None
    nationalProgram: NationalProgramModel | None
    isFavorite: bool | None
    dates: TemplateDatesModel | None
    formats: typing.Sequence[EacFormat] | None
    isTemplate: bool = True
    contactEmail: str | None
    contactPhone: str | None
    contactUrl: str | None
    contactForm: educational_models.OfferContactFormEnum | None

    @classmethod
    def build(
        cls,
        offer: educational_models.CollectiveOfferTemplate,
        is_favorite: bool,
        offerVenue: offerers_models.Venue | None = None,
    ) -> "CollectiveOfferTemplateResponseModel":
        if offer.start and offer.end:
            dates = TemplateDatesModel(start=offer.start, end=offer.end)
        else:
            dates = None

        return cls(
            id=offer.id,
            description=offer.description,
            isExpired=offer.hasBookingLimitDatetimesPassed,
            isSoldOut=False,
            name=offer.name,
            venue=offer.venue,
            students=offer.students,
            offerVenue=CollectiveOfferOfferVenue(
                name=offerVenue.name if offerVenue else None,
                publicName=offerVenue.publicName if offerVenue else None,
                address=offerVenue.street if offerVenue else None,
                postalCode=offerVenue.postalCode if offerVenue else None,
                city=offerVenue.city if offerVenue else None,
                **offer.offerVenue,
            ),
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
            dates=dates,
            formats=offer.get_formats(),
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            contactUrl=offer.contactUrl,
            contactForm=offer.contactForm,
        )
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True, json_encoders={datetime: format_into_utc_date}, use_enum_values=True)


class ListCollectiveOfferTemplateResponseModel(BaseModel):
    collectiveOffers: list[CollectiveOfferTemplateResponseModel]
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={datetime: format_into_utc_date})


class CollectiveRequestResponseModel(BaseModel):
    id: int
    email: str
    phone_number: str | None
    requested_date: date | None
    total_students: int | None
    total_teachers: int | None
    comment: str
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, json_encoders={datetime: format_into_utc_date})


class PostCollectiveRequestBodyModel(BaseModel):
    phone_number: str | None
    requested_date: date | None
    total_students: int | None
    total_teachers: int | None
    comment: str

    _validate_phone_number = validation.phone_number_validator("phone_number", nullable=True)
    model_config = ConfigDict(alias_generator=to_camel)


class GetTemplateIdsModel(BaseModel):
    ids: typing.Sequence[int]

    @model_validator(mode="before")
    @classmethod
    def format_ids(cls, values: dict) -> dict:
        ids = values.get("ids")
        if not ids:
            return values

        if not isinstance(ids, list):
            values["ids"] = [ids]

        return values
