import logging
import typing
from datetime import date
from datetime import datetime

import pydantic

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models
from pcapi.core.finance.utils import to_cents
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization.collective_offers_serialize import GetCollectiveOfferLocationModel
from pcapi.routes.serialization.national_programs import NationalProgramResponseModel
from pcapi.serialization import utils


logger = logging.getLogger(__name__)


class CollectiveOfferDatesModel(HttpBodyModel):
    start: datetime
    end: datetime


class OfferManagingOffererResponse(HttpBodyModel):
    name: str


class CollectiveAdditionalFeeResponse(HttpBodyModel):
    type: models.CollectiveAdditionalFeeType
    label: str | None
    amount: int

    @pydantic.field_validator("amount", mode="before")
    def validate_amount(cls, value: typing.Any) -> int:
        return to_cents(value)


class OfferStockResponse(HttpBodyModel):
    id: int
    startDatetime: datetime | None = None
    endDatetime: datetime | None = None
    bookingLimitDatetime: datetime | None = None
    price: int
    servicePrice: int
    collective_additional_fees: list[CollectiveAdditionalFeeResponse]
    numberOfTickets: int
    numberOfTeachers: int
    priceDetail: str | None = pydantic.Field(default=None, alias="educationalPriceDetail")

    @pydantic.field_validator("price", "servicePrice", mode="before")
    def validate_price(cls, value: typing.Any) -> int:
        return to_cents(value)


class OfferVenueCoordinates(HttpBodyModel):
    latitude: float
    longitude: float


class OfferVenueResponse(HttpBodyModel):
    id: int
    address: str
    city: str
    name: str
    postalCode: str
    departmentCode: str
    publicName: str
    coordinates: OfferVenueCoordinates
    managingOfferer: OfferManagingOffererResponse
    adageId: str | None
    imgUrl: str | None

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> typing.Self:
        return cls(
            id=venue.id,
            address=venue.offererAddress.address.street,
            city=venue.offererAddress.address.city,
            name=venue.name,
            postalCode=venue.offererAddress.address.postalCode,
            departmentCode=venue.offererAddress.address.departmentCode,
            publicName=venue.publicName,
            coordinates=OfferVenueCoordinates(
                latitude=float(venue.offererAddress.address.latitude),
                longitude=float(venue.offererAddress.address.longitude),
            ),
            managingOfferer=OfferManagingOffererResponse(name=venue.managingOfferer.name),
            adageId=venue.adageId,
            imgUrl=venue.bannerUrl,
        )


class OfferDomain(HttpBodyModel):
    id: int
    name: str


class EducationalInstitutionResponseModel(HttpBodyModel):
    id: int
    name: str
    postalCode: str
    city: str
    institutionType: str


class EducationalRedactorResponseModel(HttpBodyModel):
    email: str
    firstName: str | None
    lastName: str | None
    civility: str | None


class CollectiveOfferBaseReponseModel(HttpBodyModel):
    id: int
    description: str
    name: str
    venue: OfferVenueResponse
    students: list[models.StudentLevels]
    location: GetCollectiveOfferLocationModel
    contactEmail: str | None
    contactPhone: str | None
    durationMinutes: int | None
    educationalPriceDetail: str | None = None
    domains: list[OfferDomain]
    interventionArea: list[str]
    imageUrl: str | None
    imageCredit: str | None
    nationalProgram: NationalProgramResponseModel | None
    formats: list[EacFormat]
    isTemplate: bool
    # accessibility fields
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None

    model_config = pydantic.ConfigDict(use_enum_values=True)


class CollectiveOfferResponseModel(CollectiveOfferBaseReponseModel):
    stock: OfferStockResponse
    educationalInstitution: EducationalInstitutionResponseModel | None
    teacher: EducationalRedactorResponseModel | None
    additionalDetails: str | None

    @classmethod
    def build(cls, offer: models.CollectiveOffer) -> typing.Self:
        stock = OfferStockResponse.model_validate(offer.collectiveStock)
        venue = OfferVenueResponse.build(offer.venue)
        location = GetCollectiveOfferLocationModel.build(offer)
        domains = [OfferDomain.model_validate(domain) for domain in offer.domains]
        institution = (
            EducationalInstitutionResponseModel.model_validate(offer.institution) if offer.institution else None
        )
        teacher = EducationalRedactorResponseModel.model_validate(offer.teacher) if offer.teacher else None
        program = NationalProgramResponseModel.model_validate(offer.nationalProgram) if offer.nationalProgram else None

        return cls(
            id=offer.id,
            description=offer.description,
            name=offer.name,
            stock=stock,
            venue=venue,
            students=offer.students,
            location=location,
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            durationMinutes=offer.durationMinutes,
            educationalPriceDetail=offer.collectiveStock.priceDetail,
            domains=domains,
            educationalInstitution=institution,
            interventionArea=offer.interventionArea,
            imageUrl=offer.imageUrl,
            imageCredit=offer.imageCredit,
            teacher=teacher,
            nationalProgram=program,
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
            formats=offer.formats,
            isTemplate=False,
            additionalDetails=offer.additionalDetails,
        )


class ListCollectiveOffersResponseModel(HttpBodyModel):
    collectiveOffers: list[CollectiveOfferResponseModel]


class CollectiveOfferTemplateResponseModel(CollectiveOfferBaseReponseModel):
    isFavorite: bool | None = None
    dates: CollectiveOfferDatesModel | None = None
    contactUrl: str | None = None
    contactForm: models.OfferContactFormEnum | None = None

    @classmethod
    def build(cls, offer: models.CollectiveOfferTemplate, is_favorite: bool) -> typing.Self:
        if offer.start and offer.end:
            dates = CollectiveOfferDatesModel(start=offer.start, end=offer.end)
        else:
            dates = None

        venue = OfferVenueResponse.build(offer.venue)
        location = GetCollectiveOfferLocationModel.build(offer)
        domains = [OfferDomain.model_validate(domain) for domain in offer.domains]
        program = NationalProgramResponseModel.model_validate(offer.nationalProgram) if offer.nationalProgram else None

        return cls(
            id=offer.id,
            description=offer.description,
            name=offer.name,
            venue=venue,
            students=offer.students,
            location=location,
            durationMinutes=offer.durationMinutes,
            educationalPriceDetail=offer.priceDetail,
            domains=domains,
            interventionArea=offer.interventionArea,
            imageUrl=offer.imageUrl,
            imageCredit=offer.imageCredit,
            nationalProgram=program,
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


class ListCollectiveOfferTemplateResponseModel(HttpBodyModel):
    collectiveOffers: list[CollectiveOfferTemplateResponseModel]


class CollectiveRequestResponseModel(HttpBodyModel):
    id: int


class PostCollectiveRequestBodyModel(HttpBodyModel):
    phone_number: str | None
    requested_date: date | None
    total_students: int | None
    total_teachers: int | None
    comment: str

    @pydantic.field_validator("phone_number", mode="after")
    def validate_phone_number(cls, phone_number: str | None) -> str | None:
        return utils.validate_phone_number_nullable(phone_number)


class GetTemplateIdsModel(HttpBodyModel):
    ids: typing.Annotated[list[int], utils.ArgsAsListBeforeValidator]
