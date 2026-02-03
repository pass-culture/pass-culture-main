import logging
import typing
from datetime import date
from datetime import datetime

from pydantic.v1 import Field
from pydantic.v1 import root_validator
from pydantic.v1.class_validators import validator

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.native.v1.serialization import common_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
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
    publicName: str
    coordinates: common_models.Coordinates
    managingOfferer: OfferManagingOffererResponse
    adageId: str | None
    bannerUrl: str | None = Field(alias="imgUrl")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @classmethod
    def from_orm(cls: type["OfferVenueResponse"], venue: offerers_models.Venue) -> "OfferVenueResponse":
        return cls(
            id=venue.id,
            address=venue.offererAddress.address.street,
            city=venue.offererAddress.address.city,
            name=venue.name,
            postalCode=venue.offererAddress.address.postalCode,
            departmentCode=venue.offererAddress.address.departmentCode,
            publicName=venue.publicName,
            coordinates=common_models.Coordinates(
                latitude=venue.offererAddress.address.latitude,
                longitude=venue.offererAddress.address.longitude,
            ),
            managingOfferer=venue.managingOfferer,
            adageId=venue.adageId,
            imgUrl=venue.bannerUrl,
        )


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
    name: str
    venue: OfferVenueResponse
    students: list[educational_models.StudentLevels]
    location: collective_offers_serialize.GetCollectiveOfferLocationModel | None
    contactEmail: str | None
    contactPhone: str | None
    durationMinutes: int | None
    educationalPriceDetail: str | None
    domains: typing.Sequence[OfferDomain]
    interventionArea: list[str]
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
        cls: "type[CollectiveOfferResponseModel]", offer: educational_models.CollectiveOffer
    ) -> "CollectiveOfferResponseModel":
        return cls(
            id=offer.id,
            description=offer.description,
            name=offer.name,
            stock=offer.collectiveStock,
            venue=offer.venue,
            students=offer.students,
            location=collective_offers_serialize.get_collective_offer_location_model(offer),
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            durationMinutes=offer.durationMinutes,
            educationalPriceDetail=offer.collectiveStock.priceDetail,
            domains=offer.domains,
            educationalInstitution=offer.institution,
            interventionArea=offer.interventionArea,
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
    dates: collective_offers_serialize.CollectiveOfferDatesModel | None
    contactUrl: str | None
    contactForm: educational_models.OfferContactFormEnum | None

    @classmethod
    def build(
        cls: "type[CollectiveOfferTemplateResponseModel]",
        offer: educational_models.CollectiveOfferTemplate,
        is_favorite: bool,
    ) -> "CollectiveOfferTemplateResponseModel":
        if offer.start and offer.end:
            dates = collective_offers_serialize.CollectiveOfferDatesModel(start=offer.start, end=offer.end)
        else:
            dates = None

        return cls(
            id=offer.id,
            description=offer.description,
            name=offer.name,
            venue=offer.venue,
            students=offer.students,
            location=collective_offers_serialize.get_collective_offer_location_model(offer),
            durationMinutes=offer.durationMinutes,
            educationalPriceDetail=offer.priceDetail,
            domains=offer.domains,
            interventionArea=offer.interventionArea,
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


class CollectiveRequestResponseModel(HttpBodyModel):
    id: int


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
