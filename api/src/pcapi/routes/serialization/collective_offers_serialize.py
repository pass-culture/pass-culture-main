import typing
from datetime import date
from datetime import datetime

import flask
from pydantic.v1 import Field
from pydantic.v1 import root_validator
from pydantic.v1 import utils as pydantic_utils
from pydantic.v1 import validator

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import schemas as educational_schemas
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.core.shared import schemas as shared_schemas
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import base as base_serializers
from pcapi.routes.serialization import collective_history_serialize
from pcapi.routes.serialization import to_camel
from pcapi.routes.serialization.educational_institutions import EducationalInstitutionResponseModel
from pcapi.routes.serialization.national_programs import NationalProgramModel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.image_conversion import CropParams


def strip_string(s: str | None) -> str | None:
    if not s:
        return s
    return s.strip()


def empty_to_null(s: str | None) -> str | None:
    if not s:
        return None
    return s


class EmptyAsNullString(str):
    @classmethod
    def __get_validators__(cls) -> typing.Generator[typing.Callable, None, None]:
        yield strip_string
        yield empty_to_null


EmptyStringToNone = EmptyAsNullString | None


class ListCollectiveOffersQueryModel(BaseModel):
    nameOrIsbn: str | None
    offerer_id: int | None
    status: list[educational_models.CollectiveOfferDisplayedStatus] | None
    venue_id: int | None
    creation_mode: str | None
    period_beginning_date: date | None
    period_ending_date: date | None
    collective_offer_type: educational_schemas.CollectiveOfferType | None
    format: EacFormat | None
    location_type: educational_models.CollectiveLocationType | None
    offerer_address_id: int | None

    @validator("status", pre=True)
    def parse_status(cls, status: typing.Any | None) -> list[typing.Any] | None:
        # this is needed to handle the case of only one status in query filters
        if status is None or isinstance(status, list):
            return status

        return [status]

    @root_validator(skip_on_failure=True)
    def validate_location_filter(cls, values: dict) -> dict:
        location_type = values.get("location_type")
        offerer_address_id = values.get("offerer_address_id")

        if offerer_address_id is not None and location_type != educational_models.CollectiveLocationType.ADDRESS:
            raise ValueError(
                f"Cannot provide offerer_address_id when location_type is not {educational_models.CollectiveLocationType.ADDRESS.value}"
            )

        return values

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOffersStockResponseModel(BaseModel):
    hasBookingLimitDatetimePassed: bool
    remainingQuantity: int = 0  # needed for frontend tables compatibility
    bookingLimitDatetime: datetime | None
    startDatetime: datetime | None
    endDatetime: datetime | None
    price: float | None
    numberOfTickets: int | None

    class Config:
        orm_mode = True


class EducationalRedactorResponseModel(BaseModel):
    email: str | None
    firstName: str | None
    lastName: str | None
    civility: str | None

    class Config:
        orm_mode = True


class TemplateDatesModel(BaseModel):
    start: datetime
    end: datetime

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class CollectiveOffersBookingResponseModel(BaseModel):
    id: int
    booking_status: str


class CollectiveOfferResponseModel(BaseModel):
    hasBookingLimitDatetimesPassed: bool
    id: int
    isActive: bool
    isEducational: bool
    name: str
    stocks: list[CollectiveOffersStockResponseModel]
    booking: CollectiveOffersBookingResponseModel | None
    isShowcase: bool
    venue: base_serializers.ListOffersVenueResponseModel
    displayedStatus: educational_models.CollectiveOfferDisplayedStatus
    allowedActions: (
        list[educational_models.CollectiveOfferAllowedAction]
        | list[educational_models.CollectiveOfferTemplateAllowedAction]
    )
    educationalInstitution: EducationalInstitutionResponseModel | None
    imageUrl: str | None
    dates: TemplateDatesModel | None
    location: educational_schemas.GetCollectiveOfferLocationModel | None

    class Config:
        alias_generator = to_camel


class ListCollectiveOffersResponseModel(BaseModel):
    __root__: list[CollectiveOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


def serialize_collective_offers_capped(
    paginated_offers: list[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate],
) -> list[CollectiveOfferResponseModel]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers]


def _serialize_offer_paginated(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
) -> CollectiveOfferResponseModel:
    is_offer_template = isinstance(offer, educational_models.CollectiveOfferTemplate)

    stock = offer.collectiveStock if not is_offer_template else None
    serialized_stocks = [_serialize_stock(stock)]

    last_booking = stock.lastBooking if stock is not None else None
    if last_booking is not None:
        serialized_last_booking = CollectiveOffersBookingResponseModel(
            id=last_booking.id,
            booking_status=last_booking.status.value,
        )
    else:
        serialized_last_booking = None

    return CollectiveOfferResponseModel(
        hasBookingLimitDatetimesPassed=offer.hasBookingLimitDatetimesPassed if not is_offer_template else False,
        id=offer.id,
        isActive=offer.isActive,
        isEducational=True,
        name=offer.name,
        stocks=serialized_stocks,
        booking=serialized_last_booking,
        venue=_serialize_venue(offer.venue),
        displayedStatus=offer.displayedStatus,
        allowedActions=offer.allowedActions,
        isShowcase=is_offer_template,
        educationalInstitution=offer.institution if not is_offer_template else None,
        imageUrl=offer.imageUrl,
        dates=offer.dates,  # type: ignore[arg-type]
        location=get_collective_offer_location_model(offer),
    )


def _serialize_stock(stock: educational_models.CollectiveStock | None) -> CollectiveOffersStockResponseModel:
    if stock is not None:
        return CollectiveOffersStockResponseModel.from_orm(stock)

    return CollectiveOffersStockResponseModel(
        hasBookingLimitDatetimePassed=False,
        remainingQuantity=1,
        startDatetime=None,
        endDatetime=None,
        bookingLimitDatetime=None,
        price=None,
        numberOfTickets=None,
    )


def _serialize_venue(venue: offerers_models.Venue) -> base_serializers.ListOffersVenueResponseModel:
    if venue.offererAddress is not None:
        department_code = venue.offererAddress.address.departmentCode
    else:
        # TODO(OA): remove this when the virtual venues are migrated
        department_code = None

    return base_serializers.ListOffersVenueResponseModel(
        id=venue.id,
        isVirtual=venue.isVirtual,
        name=venue.name,
        offererName=venue.managingOfferer.name,
        publicName=venue.publicName,
        departementCode=department_code,
    )


def _get_serialize_last_booking(
    bookings: list[educational_models.CollectiveBooking],
) -> CollectiveOffersBookingResponseModel | None:
    if len(bookings) == 0:
        return None
    last_booking = sorted(bookings, key=lambda b: b.dateCreated, reverse=True)[0]
    return CollectiveOffersBookingResponseModel(
        id=last_booking.id,
        booking_status=last_booking.status.value,
    )


class OfferDomain(BaseModel):
    id: int
    name: str

    class Config:
        alias_generator = to_camel
        orm_mode = True


class GetCollectiveOfferManagingOffererResponseModel(BaseModel):
    id: int
    name: str
    siren: str
    allowedOnAdage: bool

    class Config:
        orm_mode = True


class GetCollectiveOfferVenueResponseModel(BaseModel):
    departementCode: str | None
    id: int
    managingOfferer: GetCollectiveOfferManagingOffererResponseModel
    name: str
    publicName: str | None
    bannerUrl: str | None = Field(alias="imgUrl")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        allow_population_by_field_name = True

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetCollectiveOfferVenueResponseModel":
        if venue.offererAddress is not None:
            department_code = venue.offererAddress.address.departmentCode
        else:
            # TODO(OA): remove this when the virtual venues are migrated
            department_code = None

        return cls(
            departementCode=department_code,
            id=venue.id,
            managingOfferer=venue.managingOfferer,
            name=venue.name,
            publicName=venue.publicName,
            imgUrl=venue.bannerUrl,
        )


class CollectiveOfferOfferVenueResponseModel(BaseModel):
    addressType: educational_models.OfferAddressType
    otherAddress: str
    venueId: int | None

    _validated_venue_id = validator("venueId", pre=True, allow_reuse=True)(educational_schemas.validate_venue_id)


class GetCollectiveOfferCollectiveStockResponseModel(BaseModel):
    id: int
    isSoldOut: bool = Field(alias="isBooked")
    is_cancellable_from_offerer: bool = Field(alias="isCancellable")
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float
    numberOfTickets: int | None
    priceDetail: educational_schemas.PriceDetail | None = Field(alias="educationalPriceDetail")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetCollectiveOfferBookingResponseModel(BaseModel):
    id: int
    dateCreated: datetime
    status: educational_models.CollectiveBookingStatus
    educationalRedactor: EducationalRedactorResponseModel | None
    cancellationLimitDate: datetime
    cancellationReason: educational_models.CollectiveBookingCancellationReasons | None
    confirmationLimitDate: datetime

    class Config:
        orm_mode = True


def get_collective_offer_location_model(
    offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
) -> educational_schemas.GetCollectiveOfferLocationModel | None:
    if offer.locationType is None:
        return None

    address = None
    oa = offer.offererAddress
    if oa is not None:
        address = shared_schemas.AddressResponseIsLinkedToVenueModel(
            **address_serialize.retrieve_address_info_from_oa(oa),
            label=offer.venue.common_name if oa._isLinkedToVenue else oa.label,
            isLinkedToVenue=oa._isLinkedToVenue,
        )

    return educational_schemas.GetCollectiveOfferLocationModel(
        locationType=offer.locationType, locationComment=offer.locationComment, address=address
    )


class GetCollectiveOfferBaseResponseGetterDict(pydantic_utils.GetterDict):
    def get(self, key: str, default: typing.Any | None = None) -> typing.Any:
        if key == "location":
            return get_collective_offer_location_model(self._obj)

        if key == "history":
            return collective_history_serialize.get_collective_offer_history(self._obj)

        return super().get(key, default)


class GetCollectiveOfferBaseResponseModel(BaseModel, shared_schemas.AccessibilityComplianceMixin):
    bookingEmails: list[str]
    dateCreated: datetime
    description: str
    durationMinutes: int | None
    students: list[educational_models.StudentLevels]
    # offerVenue will be replaced with location, for now we send both
    offerVenue: CollectiveOfferOfferVenueResponseModel
    location: educational_schemas.GetCollectiveOfferLocationModel | None
    contactEmail: str | None
    contactPhone: str | None
    hasBookingLimitDatetimesPassed: bool
    isActive: bool
    id: int
    name: str
    venue: GetCollectiveOfferVenueResponseModel
    displayedStatus: educational_models.CollectiveOfferDisplayedStatus
    domains: list[OfferDomain]
    interventionArea: list[str]
    is_cancellable_from_offerer: bool = Field(alias="isCancellable")
    imageCredit: str | None
    imageUrl: str | None
    nationalProgram: NationalProgramModel | None
    formats: typing.Sequence[EacFormat]
    isNonFreeOffer: bool | None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True
        getter_dict = GetCollectiveOfferBaseResponseGetterDict


class GetCollectiveOfferTemplateResponseModel(GetCollectiveOfferBaseResponseModel):
    priceDetail: educational_schemas.PriceDetail | None = Field(alias="educationalPriceDetail")
    dates: TemplateDatesModel | None
    isTemplate: bool = True
    contactEmail: str | None
    contactPhone: str | None
    contactUrl: str | None
    contactForm: educational_models.OfferContactFormEnum | None
    allowedActions: list[educational_models.CollectiveOfferTemplateAllowedAction]


class CollectiveOfferRedactorModel(BaseModel):
    firstName: str | None
    lastName: str | None
    email: str


class CollectiveOfferInstitutionModel(BaseModel):
    institutionId: str
    institutionType: str
    name: str
    city: str
    postalCode: str


class GetCollectiveOfferRequestResponseModel(BaseModel):
    redactor: CollectiveOfferRedactorModel
    requestedDate: date | None
    totalStudents: int | None
    totalTeachers: int | None
    phoneNumber: str | None
    comment: str
    dateCreated: date | None
    institution: CollectiveOfferInstitutionModel

    class Config:
        allow_population_by_field_name = True


class GetCollectiveOfferProviderResponseModel(BaseModel):
    name: str

    class Config:
        orm_mode = True


class GetCollectiveOfferResponseModel(GetCollectiveOfferBaseResponseModel):
    isBookable: bool
    collectiveStock: GetCollectiveOfferCollectiveStockResponseModel | None
    lastBooking: GetCollectiveOfferBookingResponseModel | None = Field(alias="booking")
    institution: EducationalInstitutionResponseModel | None
    templateId: int | None
    teacher: EducationalRedactorResponseModel | None
    isPublicApi: bool
    provider: GetCollectiveOfferProviderResponseModel | None
    isTemplate: bool = False
    dates: TemplateDatesModel | None
    allowedActions: list[educational_models.CollectiveOfferAllowedAction]
    history: collective_history_serialize.CollectiveOfferHistory


class CollectiveOfferResponseIdModel(BaseModel):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PatchCollectiveOfferActiveStatusBodyModel(BaseModel):
    is_active: bool
    ids: list[int]

    class Config:
        alias_generator = to_camel


class PatchCollectiveOfferArchiveBodyModel(BaseModel):
    ids: list[int]


class PatchCollectiveOfferEducationalInstitution(BaseModel):
    educational_institution_id: int
    teacher_email: str | None

    class Config:
        alias_generator = to_camel
        extra = "allow"


class AttachImageFormModel(BaseModel):
    credit: str
    cropping_rect_x: float
    cropping_rect_y: float
    cropping_rect_height: float
    cropping_rect_width: float

    class Config:
        alias_generator = to_camel

    @property
    def crop_params(self) -> CropParams:
        return CropParams.build(
            x_crop_percent=self.cropping_rect_x,
            y_crop_percent=self.cropping_rect_y,
            height_crop_percent=self.cropping_rect_height,
            width_crop_percent=self.cropping_rect_width,
        )

    def get_image_as_bytes(self, request: flask.Request) -> bytes:
        """
        Get the image from the POSTed data (request)
        Only the max size is checked at this stage, and possibly the content type header
        """
        if "thumb" in request.files:
            blob = request.files["thumb"]
            image_as_bytes = blob.read()
            offers_validation.check_image_size(image_as_bytes)
            return image_as_bytes

        raise offers_validation.exceptions.MissingImage()


class AttachImageResponseModel(BaseModel):
    imageUrl: str

    class Config:
        orm_mode = True
