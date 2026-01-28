import typing
from datetime import date
from datetime import datetime

import flask
from pydantic.v1 import AnyHttpUrl
from pydantic.v1 import ConstrainedStr
from pydantic.v1 import EmailStr
from pydantic.v1 import Field
from pydantic.v1 import root_validator
from pydantic.v1 import utils as pydantic_utils
from pydantic.v1 import validator

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import validation as educational_validation
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import validation as offers_validation
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import collective_history_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.educational_institutions import EducationalInstitutionResponseModel
from pcapi.routes.serialization.national_programs import NationalProgramModel
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.serialization import utils
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.image_conversion import CropParams


class ListCollectiveOffersQueryModel(ConfiguredBaseModel):
    name: str | None
    offerer_id: int | None
    status: list[educational_models.CollectiveOfferDisplayedStatus] | None
    venue_id: int | None
    period_beginning_date: date | None
    period_ending_date: date | None
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
        extra = "forbid"


class CollectiveOfferStockResponseModel(ConfiguredBaseModel):
    bookingLimitDatetime: datetime | None
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


class CollectiveOfferDatesModel(BaseModel):
    start: datetime
    end: datetime

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class GetCollectiveOfferLocationModel(BaseModel):
    locationType: educational_models.CollectiveLocationType
    locationComment: str | None
    location: address_serialize.LocationResponseModel | None


def _serialize_venue(venue: offerers_models.Venue) -> venues_serialize.ListOffersVenueResponseModel:
    department_code = venue.offererAddress.address.departmentCode

    return venues_serialize.ListOffersVenueResponseModel(
        id=venue.id,
        isVirtual=venue.isVirtual,
        name=venue.name,
        offererName=venue.managingOfferer.name,
        publicName=venue.publicName,
        departementCode=department_code,
    )


class BaseCollectiveOfferResponseModel(ConfiguredBaseModel):
    id: int
    name: str
    venue: venues_serialize.ListOffersVenueResponseModel
    displayedStatus: educational_models.CollectiveOfferDisplayedStatus
    imageUrl: str | None
    location: GetCollectiveOfferLocationModel
    dates: CollectiveOfferDatesModel | None


class CollectiveOfferResponseModel(BaseCollectiveOfferResponseModel):
    allowedActions: list[educational_models.CollectiveOfferAllowedAction]
    stock: CollectiveOfferStockResponseModel | None
    educationalInstitution: EducationalInstitutionResponseModel | None

    @classmethod
    def build(
        cls: type["CollectiveOfferResponseModel"], offer: educational_models.CollectiveOffer
    ) -> "CollectiveOfferResponseModel":
        stock = offer.collectiveStock
        serialized_stock = CollectiveOfferStockResponseModel.from_orm(stock) if stock is not None else None

        start, end = offer.start, offer.end
        if start is not None and end is not None:
            dates = CollectiveOfferDatesModel(start=start, end=end)
        else:
            dates = None

        return cls(
            id=offer.id,
            name=offer.name,
            venue=_serialize_venue(offer.venue),
            displayedStatus=offer.displayedStatus,
            allowedActions=offer.allowedActions,
            imageUrl=offer.imageUrl,
            location=get_collective_offer_location_model(offer),
            stock=serialized_stock,
            educationalInstitution=offer.institution,
            dates=dates,
        )


class ListCollectiveOffersResponseModel(ConfiguredBaseModel):
    __root__: list[CollectiveOfferResponseModel]


class CollectiveOfferTemplateResponseModel(BaseCollectiveOfferResponseModel):
    allowedActions: list[educational_models.CollectiveOfferTemplateAllowedAction]
    dates: CollectiveOfferDatesModel | None

    @classmethod
    def build(
        cls: type["CollectiveOfferTemplateResponseModel"], offer: educational_models.CollectiveOfferTemplate
    ) -> "CollectiveOfferTemplateResponseModel":
        start, end = offer.start, offer.end
        if start is not None and end is not None:
            dates = CollectiveOfferDatesModel(start=start, end=end)
        else:
            dates = None

        return cls(
            id=offer.id,
            name=offer.name,
            venue=_serialize_venue(offer.venue),
            displayedStatus=offer.displayedStatus,
            allowedActions=offer.allowedActions,
            imageUrl=offer.imageUrl,
            dates=dates,
            location=get_collective_offer_location_model(offer),
        )


class ListCollectiveOfferTemplatesResponseModel(ConfiguredBaseModel):
    __root__: list[CollectiveOfferTemplateResponseModel]


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

    class Config:
        orm_mode = True


class GetCollectiveOfferVenueResponseModel(BaseModel):
    departementCode: str | None
    id: int
    managingOfferer: GetCollectiveOfferManagingOffererResponseModel
    name: str
    publicName: str
    bannerUrl: str | None = Field(alias="imgUrl")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        allow_population_by_field_name = True

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "GetCollectiveOfferVenueResponseModel":
        return cls(
            departementCode=venue.offererAddress.address.departmentCode,
            id=venue.id,
            managingOfferer=venue.managingOfferer,
            name=venue.name,
            publicName=venue.publicName,
            imgUrl=venue.bannerUrl,
        )


class CollectiveOfferLocationModel(BaseModel):
    locationType: educational_models.CollectiveLocationType
    locationComment: str | None
    location: address_serialize.LocationBodyModel | address_serialize.LocationOnlyOnVenueBodyModel | None

    @validator("locationComment")
    def validate_location_comment(cls, location_comment: str | None, values: dict) -> str | None:
        location_type = values.get("locationType")
        if location_type != educational_models.CollectiveLocationType.TO_BE_DEFINED and location_comment is not None:
            raise ValueError("locationComment is not allowed for the provided locationType")
        return location_comment

    @validator("location")
    def validate_location(
        cls,
        address: address_serialize.LocationBodyModel | address_serialize.LocationOnlyOnVenueBodyModel | None,
        values: dict,
    ) -> address_serialize.LocationBodyModel | address_serialize.LocationOnlyOnVenueBodyModel | None:
        location_type = values.get("locationType")
        if (
            location_type
            in (
                educational_models.CollectiveLocationType.SCHOOL,
                educational_models.CollectiveLocationType.TO_BE_DEFINED,
            )
            and address is not None
        ):
            raise ValueError("address is not allowed for the provided locationType")

        if location_type == educational_models.CollectiveLocationType.ADDRESS and address is None:
            raise ValueError("address is required for the provided locationType")
        return address


class PriceDetail(ConstrainedStr):
    max_length: int = 1_000


class GetCollectiveOfferCollectiveStockResponseModel(BaseModel):
    id: int
    startDatetime: datetime | None
    endDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float
    numberOfTickets: int | None
    priceDetail: PriceDetail | None = Field(alias="educationalPriceDetail")

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
) -> GetCollectiveOfferLocationModel:
    location = None
    oa = offer.offererAddress
    venue = offer.venue
    if oa is not None:
        is_venue_location = False
        if venue.offererAddress.addressId == oa.addressId and (oa.label is None or oa.label == venue.publicName):
            is_venue_location = True
        location = address_serialize.LocationResponseModel(
            **address_serialize.retrieve_address_info_from_oa(oa),
            label=offer.venue.common_name if is_venue_location else oa.label,
            isVenueLocation=is_venue_location,
        )

    return GetCollectiveOfferLocationModel(
        locationType=offer.locationType, locationComment=offer.locationComment, location=location
    )


class GetCollectiveOfferBaseResponseGetterDict(pydantic_utils.GetterDict):
    def get(self, key: str, default: typing.Any | None = None) -> typing.Any:
        offer = self._obj

        if key == "location":
            return get_collective_offer_location_model(offer)

        if key == "history":
            return collective_history_serialize.get_collective_offer_history(offer)

        return super().get(key, default)


class GetCollectiveOfferBaseResponseModel(BaseModel, AccessibilityComplianceMixin):
    bookingEmails: list[str]
    dateCreated: datetime
    description: str
    durationMinutes: int | None
    students: list[educational_models.StudentLevels]
    location: GetCollectiveOfferLocationModel
    contactEmail: str | None
    contactPhone: str | None
    id: int
    name: str
    venue: GetCollectiveOfferVenueResponseModel
    displayedStatus: educational_models.CollectiveOfferDisplayedStatus
    domains: list[OfferDomain]
    interventionArea: list[str]
    imageCredit: str | None
    imageUrl: str | None
    nationalProgram: NationalProgramModel | None
    formats: typing.Sequence[EacFormat]

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True
        getter_dict = GetCollectiveOfferBaseResponseGetterDict


class GetCollectiveOfferTemplateResponseModel(GetCollectiveOfferBaseResponseModel):
    priceDetail: PriceDetail | None = Field(alias="educationalPriceDetail")
    dates: CollectiveOfferDatesModel | None
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
    collectiveStock: GetCollectiveOfferCollectiveStockResponseModel | None
    lastBooking: GetCollectiveOfferBookingResponseModel | None = Field(alias="booking")
    institution: EducationalInstitutionResponseModel | None
    templateId: int | None
    teacher: EducationalRedactorResponseModel | None
    isPublicApi: bool
    provider: GetCollectiveOfferProviderResponseModel | None
    isTemplate: bool = False
    dates: CollectiveOfferDatesModel | None
    allowedActions: list[educational_models.CollectiveOfferAllowedAction]
    history: collective_history_serialize.CollectiveOfferHistory


class CollectiveOfferResponseIdModel(BaseModel):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


def validate_intervention_area_with_location(
    intervention_area: list[str] | None, location: CollectiveOfferLocationModel
) -> None:
    # handle the case where it is None and []
    if intervention_area:
        if location.locationType == educational_models.CollectiveLocationType.ADDRESS:
            raise ValueError("intervention_area must be empty")

        if any(area for area in intervention_area if area not in ALL_INTERVENTION_AREA):
            raise ValueError("intervention_area must be a valid area")
    else:
        if location.locationType in (
            educational_models.CollectiveLocationType.TO_BE_DEFINED,
            educational_models.CollectiveLocationType.SCHOOL,
        ):
            raise ValueError("intervention_area is required and must not be empty")


class DateRangeModel(BaseModel):
    start: datetime
    end: datetime

    @validator("start")
    def validate_start(cls, start: datetime) -> datetime:
        return utils.without_timezone(start)

    @validator("end")
    def validate_end(cls, end: datetime) -> datetime:
        return utils.without_timezone(end)

    @root_validator(skip_on_failure=True)
    def validate_end_before_start(cls, values: dict) -> dict:
        if values["start"] > values["end"]:
            raise ValueError("end before start")

        return values


class DateRangeOnCreateModel(DateRangeModel):
    @validator("start")
    def validate_start(cls, start: datetime) -> datetime:
        start = super().validate_start(start)

        if start.date() < date.today():
            raise ValueError("start date can't be passed")
        return start


class PostCollectiveOfferBodyModel(BaseModel):
    venue_id: int
    name: str
    booking_emails: list[EmailStr]
    description: str
    domains: list[int]
    duration_minutes: int | None
    audio_disability_compliant: bool = False
    mental_disability_compliant: bool = False
    motor_disability_compliant: bool = False
    visual_disability_compliant: bool = False
    students: list[educational_models.StudentLevels]
    location: CollectiveOfferLocationModel
    contact_email: EmailStr | None
    contact_phone: str | None
    intervention_area: list[str] | None
    template_id: int | None
    nationalProgramId: int | None
    formats: typing.Sequence[EacFormat]

    @validator("students")
    def validate_students(cls, students: list[str]) -> list[educational_models.StudentLevels]:
        return shared_offers.validate_students(students)

    @validator("name")
    def validate_name(cls, name: str) -> str:
        educational_validation.check_collective_offer_name_length_is_valid(name)
        return name

    @validator("description")
    def validate_description(cls, description: str) -> str:
        educational_validation.check_collective_offer_description_length_is_valid(description)
        return description

    @validator("domains")
    def validate_domains(cls, domains: list[str]) -> list[str]:
        if not domains:
            raise ValueError("domains must have at least one value")
        return domains

    @validator("formats")
    def validate_formats(cls, formats: list[EacFormat]) -> list[EacFormat]:
        if len(formats) == 0:
            raise ValueError("formats must have at least one value")
        return formats

    @validator("intervention_area")
    def validate_intervention_area(cls, intervention_area: list[str] | None, values: dict) -> list[str] | None:
        location = values.get("location")
        if location is not None:
            validate_intervention_area_with_location(intervention_area, location)

        return intervention_area

    @validator("booking_emails")
    def validate_booking_emails(cls, booking_emails: list[str]) -> list[str]:
        if not booking_emails:
            raise ValueError("Un email doit etre renseigné.")
        return booking_emails

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PostCollectiveOfferTemplateBodyModel(PostCollectiveOfferBodyModel):
    price_detail: PriceDetail | None
    contact_url: AnyHttpUrl | None
    contact_form: educational_models.OfferContactFormEnum | None
    dates: DateRangeOnCreateModel | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchCollectiveOfferBodyModel(BaseModel, AccessibilityComplianceMixin):
    bookingEmails: list[EmailStr] | None
    description: str | None
    name: str | None
    students: list[educational_models.StudentLevels] | None
    location: CollectiveOfferLocationModel | None
    contactEmail: EmailStr | None
    contactPhone: str | None
    durationMinutes: int | None
    domains: list[int] | None
    interventionArea: list[str] | None
    venueId: int | None
    nationalProgramId: int | None
    formats: typing.Sequence[EacFormat] | None

    @validator("students")
    def validate_students(cls, students: list[str] | None) -> list[educational_models.StudentLevels] | None:
        if not students:
            return None
        return shared_offers.validate_students(students)

    @validator("name")
    def validate_name(cls, name: str | None) -> str | None:
        assert name is not None and name.strip() != ""
        educational_validation.check_collective_offer_name_length_is_valid(name)
        return name

    @validator("description")
    def validate_description(cls, description: str | None) -> str | None:
        if description is None:
            raise ValueError("Description cannot be NULL.")
        educational_validation.check_collective_offer_description_length_is_valid(description)
        return description

    @validator("formats")
    def validate_formats(cls, formats: list[EacFormat] | None) -> list[EacFormat]:
        if formats is None or len(formats) == 0:
            raise ValueError("formats must have at least one value")
        return formats

    @validator("domains")
    def validate_domains_collective_offer_edition(cls, domains: list[int] | None) -> list[int] | None:
        if domains is None or len(domains) == 0:
            raise ValueError("domains must have at least one value")
        return domains

    @validator("interventionArea")
    def validate_intervention_area(cls, intervention_area: list[str] | None, values: dict) -> list[str] | None:
        location = values.get("location")
        if location is not None:
            validate_intervention_area_with_location(intervention_area, location)

        return intervention_area

    @validator("bookingEmails")
    def validate_booking_emails(cls, booking_emails: list[str]) -> list[str]:
        if not booking_emails:
            raise ValueError("Un email doit être renseigné.")
        return booking_emails

    @validator("venueId", allow_reuse=True)
    def validate_venue_id(cls, venue_id: int | None) -> int | None:
        if venue_id is None:
            raise ValueError("venue_id cannot be NULL.")
        return venue_id

    @validator("location")
    def validate_location(cls, location: CollectiveOfferLocationModel | None) -> CollectiveOfferLocationModel | None:
        if location is None:
            raise ValueError("location cannot be NULL.")

        return location

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchCollectiveOfferTemplateBodyModel(PatchCollectiveOfferBodyModel):
    priceDetail: PriceDetail | None
    domains: list[int] | None
    dates: DateRangeModel | None
    contactUrl: str | None
    contactForm: educational_models.OfferContactFormEnum | None

    @validator("domains")
    def validate_domains_collective_offer_template_edition(
        cls,
        domains: list[int] | None,
    ) -> list[int] | None:
        if domains is not None and len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    @root_validator
    def validate_contact_fields(cls, values: dict) -> dict:
        url = values.get("contactUrl")
        form = values.get("contactForm")

        if url and form:
            raise ValueError("error: url and form are both not null")

        return values

    class Config:
        alias_generator = to_camel
        extra = "forbid"


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
