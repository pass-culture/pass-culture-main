import logging
import typing
from datetime import date
from datetime import datetime
from decimal import Decimal

from pydantic.v1 import Field
from pydantic.v1 import root_validator
from pydantic.v1.class_validators import validator

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.native.v1.serialization import common_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization.national_programs import NationalProgramModel
from pcapi.routes.shared import validation
from pcapi.routes.shared.price import convert_to_cent
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class OfferManagingOffererResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OfferStockResponse(BaseModel):
    id: int
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    isBookable: bool
    price: int
    numberOfTickets: int | None
    priceDetail: str | None = Field(alias="educationalPriceDetail")

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}


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

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "OfferVenueResponse":
        if venue.offererAddress is not None:
            source_address = venue.offererAddress.address
            address = source_address.street
            city = source_address.city
            postal_code = source_address.postalCode
            department_code = source_address.departmentCode
            coordinates = common_models.Coordinates(
                latitude=source_address.latitude, longitude=source_address.longitude
            )
        else:
            # TODO(OA): remove this when the virtual venues are migrated
            address = None
            city = None
            postal_code = None
            department_code = None
            coordinates = common_models.Coordinates(latitude=None, longitude=None)

        return cls(
            id=venue.id,
            address=address,
            city=city,
            name=venue.name,
            postalCode=postal_code,
            departmentCode=department_code,
            publicName=venue.publicName,
            coordinates=coordinates,
            managingOfferer=venue.managingOfferer,
            adageId=venue.adageId,
            distance=None,
            imgUrl=venue.bannerUrl,
        )


class CollectiveOfferOfferVenue(BaseModel):
    addressType: educational_models.OfferAddressType
    otherAddress: str
    venueId: int | None
    name: str | None
    publicName: str | None
    address: str | None
    postalCode: str | None
    city: str | None
    distance: Decimal | None

    _validated_venue_id = validator("venueId", pre=True, allow_reuse=True)(
        collective_offers_serialize.validate_venue_id
    )

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


class CollectiveOfferBaseReponseModel(BaseModel, common_models.AccessibilityComplianceMixin):
    id: int
    description: str | None
    isExpired: bool
    isSoldOut: bool
    name: str
    venue: OfferVenueResponse
    students: list[educational_models.StudentLevels]
    # offerVenue will be replaced with location, for now we send both
    offerVenue: CollectiveOfferOfferVenue
    location: collective_offers_serialize.GetCollectiveOfferLocationModel | None
    contactEmail: str | None
    contactPhone: str | None
    durationMinutes: int | None
    educationalPriceDetail: str | None
    domains: typing.Sequence[OfferDomain]
    interventionArea: list[str]
    imageCredit: str | None
    imageUrl: str | None
    nationalProgram: NationalProgramModel | None
    formats: typing.Sequence[EacFormat]
    isTemplate: bool

    class Config:
        alias_generator = to_camel
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True
        extra = "forbid"


class CollectiveOfferResponseModel(CollectiveOfferBaseReponseModel):
    collectiveStock: OfferStockResponse = Field(alias="stock")
    institution: EducationalInstitutionResponseModel | None = Field(alias="educationalInstitution")
    teacher: EducationalRedactorResponseModel | None

    @classmethod
    def build(
        cls: "type[CollectiveOfferResponseModel]",
        offer: educational_models.CollectiveOffer,
        offerVenue: offerers_models.Venue | None = None,
    ) -> "CollectiveOfferResponseModel":
        offer_venue_address = offerVenue.offererAddress.address if offerVenue and offerVenue.offererAddress else None

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
                address=offer_venue_address.street if offer_venue_address else None,
                postalCode=offer_venue_address.postalCode if offer_venue_address else None,
                city=offer_venue_address.city if offer_venue_address else None,
                distance=None,
                addressType=offer.offerVenue["addressType"],  # type: ignore[arg-type]
                venueId=offer.offerVenue["venueId"],
                otherAddress=offer.offerVenue["otherAddress"],
            ),
            location=collective_offers_serialize.get_collective_offer_location_model(offer),
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            durationMinutes=offer.durationMinutes,
            educationalPriceDetail=offer.collectiveStock.priceDetail,
            domains=offer.domains,
            institution=offer.institution,
            interventionArea=offer.interventionArea,
            imageCredit=offer.imageCredit,
            imageUrl=offer.imageUrl,
            teacher=offer.teacher,
            nationalProgram=offer.nationalProgram,
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
            formats=offer.formats,
            isTemplate=False,
        )


class ListCollectiveOffersResponseModel(BaseModel):
    collectiveOffers: list[CollectiveOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class CollectiveOfferTemplateResponseModel(CollectiveOfferBaseReponseModel):
    isFavorite: bool | None
    dates: collective_offers_serialize.TemplateDatesModel | None
    contactUrl: str | None
    contactForm: educational_models.OfferContactFormEnum | None

    @classmethod
    def build(
        cls: "type[CollectiveOfferTemplateResponseModel]",
        offer: educational_models.CollectiveOfferTemplate,
        is_favorite: bool,
        offerVenue: offerers_models.Venue | None = None,
    ) -> "CollectiveOfferTemplateResponseModel":
        if offer.start and offer.end:
            dates = collective_offers_serialize.TemplateDatesModel(start=offer.start, end=offer.end)
        else:
            dates = None

        offer_venue_address = offerVenue.offererAddress.address if offerVenue and offerVenue.offererAddress else None

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
                address=offer_venue_address.street if offer_venue_address else None,
                postalCode=offer_venue_address.postalCode if offer_venue_address else None,
                city=offer_venue_address.city if offer_venue_address else None,
                distance=None,
                addressType=offer.offerVenue["addressType"],  # type: ignore[arg-type]
                venueId=offer.offerVenue["venueId"],
                otherAddress=offer.offerVenue["otherAddress"],
            ),
            location=collective_offers_serialize.get_collective_offer_location_model(offer),
            durationMinutes=offer.durationMinutes,
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
            formats=offer.formats,
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            contactUrl=offer.contactUrl,
            contactForm=offer.contactForm,
            isTemplate=True,
        )


class ListCollectiveOfferTemplateResponseModel(BaseModel):
    collectiveOffers: list[CollectiveOfferTemplateResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


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

    _validate_phone_number = validation.phone_number_validator("phone_number", nullable=True)

    class Config:
        alias_generator = to_camel


class GetTemplateIdsModel(BaseModel):
    ids: typing.Sequence[int]

    @root_validator(pre=True)
    def format_ids(cls, values: dict) -> dict:
        ids = values.get("ids")
        if not ids:
            return values

        if not isinstance(ids, list):
            values["ids"] = [ids]

        return values
