import typing
from datetime import date
from datetime import datetime

import pydantic as pydantic_v2
from pydantic.v1 import ConstrainedStr
from pydantic.v1 import EmailStr
from pydantic.v1 import Field
from pydantic.v1 import root_validator
from pydantic.v1 import utils as pydantic_utils
from pydantic.v1 import validator
from spectree.models import BaseFile

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import constants
from pcapi.core.educational import models
from pcapi.core.educational import validation
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import collective_history_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.educational_institutions import EducationalInstitutionResponseModel
from pcapi.routes.serialization.national_programs import NationalProgramModel
from pcapi.routes.serialization.utils import raise_error_from_location
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.serialization import utils
from pcapi.serialization.exceptions import PydanticError
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class ListCollectiveOffersQueryModel(HttpQueryParamsModel):
    name: str | None = None
    offerer_id: int | None = None
    status: typing.Annotated[list[models.CollectiveOfferDisplayedStatus] | None, utils.args_as_list_validator] = None
    venue_id: int | None = None
    period_beginning_date: date | None = None
    period_ending_date: date | None = None
    format: EacFormat | None = None
    location_type: models.CollectiveLocationType | None = None
    offerer_address_id: int | None = None

    @pydantic_v2.model_validator(mode="after")
    def validate_location_filter(self) -> typing.Self:
        if self.offerer_address_id is not None and self.location_type != models.CollectiveLocationType.ADDRESS:
            raise PydanticError(
                f"Cannot provide offererAddressId when locationType is not {models.CollectiveLocationType.ADDRESS.value}"
            )

        return self


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
    locationType: models.CollectiveLocationType
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
    displayedStatus: models.CollectiveOfferDisplayedStatus
    imageUrl: str | None
    location: GetCollectiveOfferLocationModel
    dates: CollectiveOfferDatesModel | None


class CollectiveOfferResponseModel(BaseCollectiveOfferResponseModel):
    allowedActions: list[models.CollectiveOfferAllowedAction]
    stock: CollectiveOfferStockResponseModel | None
    educationalInstitution: EducationalInstitutionResponseModel | None

    @classmethod
    def build(
        cls: type["CollectiveOfferResponseModel"], offer: models.CollectiveOffer
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
    allowedActions: list[models.CollectiveOfferTemplateAllowedAction]
    dates: CollectiveOfferDatesModel | None

    @classmethod
    def build(
        cls: type["CollectiveOfferTemplateResponseModel"], offer: models.CollectiveOfferTemplate
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
    locationType: models.CollectiveLocationType
    locationComment: str | None
    location: address_serialize.LocationBodyModel | address_serialize.LocationOnlyOnVenueBodyModel | None

    @validator("locationComment")
    def validate_location_comment(cls, location_comment: str | None, values: dict) -> str | None:
        location_type = values.get("locationType")
        if location_type != models.CollectiveLocationType.TO_BE_DEFINED and location_comment is not None:
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
                models.CollectiveLocationType.SCHOOL,
                models.CollectiveLocationType.TO_BE_DEFINED,
            )
            and address is not None
        ):
            raise ValueError("address is not allowed for the provided locationType")

        if location_type == models.CollectiveLocationType.ADDRESS and address is None:
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
    status: models.CollectiveBookingStatus
    educationalRedactor: EducationalRedactorResponseModel | None
    cancellationLimitDate: datetime
    cancellationReason: models.CollectiveBookingCancellationReasons | None
    confirmationLimitDate: datetime

    class Config:
        orm_mode = True


def get_collective_offer_location_model(
    offer: models.CollectiveOffer | models.CollectiveOfferTemplate,
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
    students: list[models.StudentLevels]
    location: GetCollectiveOfferLocationModel
    contactEmail: str | None
    contactPhone: str | None
    id: int
    name: str
    venue: GetCollectiveOfferVenueResponseModel
    displayedStatus: models.CollectiveOfferDisplayedStatus
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
    contactForm: models.OfferContactFormEnum | None
    allowedActions: list[models.CollectiveOfferTemplateAllowedAction]


class CollectiveOfferRedactorModel(HttpBodyModel):
    firstName: str | None
    lastName: str | None
    email: str


class CollectiveOfferInstitutionModel(HttpBodyModel):
    institutionId: str
    institutionType: str
    name: str
    city: str
    postalCode: str


class GetCollectiveOfferRequestResponseModel(HttpBodyModel):
    educationalRedactor: CollectiveOfferRedactorModel = pydantic_v2.Field(alias="redactor")
    requestedDate: date | None
    totalStudents: int | None
    totalTeachers: int | None
    phoneNumber: str | None
    comment: str
    dateCreated: date
    educationalInstitution: CollectiveOfferInstitutionModel = pydantic_v2.Field(alias="institution")


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
    allowedActions: list[models.CollectiveOfferAllowedAction]
    history: collective_history_serialize.CollectiveOfferHistory


class CollectiveOfferResponseIdModel(HttpBodyModel):
    id: int


def validate_intervention_area_with_location(
    intervention_area: list[str] | None, location: CollectiveOfferLocationModel
) -> None:
    # handle the case where it is None and []
    if intervention_area:
        if location.locationType == models.CollectiveLocationType.ADDRESS:
            raise ValueError("intervention_area must be empty")

        if any(area for area in intervention_area if area not in constants.ALL_INTERVENTION_AREA):
            raise ValueError("intervention_area must be a valid area")
    else:
        if location.locationType in (
            models.CollectiveLocationType.TO_BE_DEFINED,
            models.CollectiveLocationType.SCHOOL,
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


class PostDateRangeModel(HttpBodyModel):
    start: datetime
    end: datetime

    @pydantic_v2.field_validator("start", "end")
    @classmethod
    def remove_timezone(cls, date_time: datetime) -> datetime:
        return utils.without_timezone(date_time)

    @pydantic_v2.field_validator("start")
    @classmethod
    def validate_start(cls, start: datetime) -> datetime:
        if start.date() < date.today():
            raise PydanticError("La date de début ne peut pas être dans le passé")

        return start

    @pydantic_v2.model_validator(mode="after")
    def validate_end_before_start(self) -> typing.Self:
        if self.start > self.end:
            raise PydanticError("La date de début doit être avant la date de fin")

        return self


class CollectiveOfferLocationModelV2(HttpBodyModel):
    locationType: models.CollectiveLocationType
    locationComment: str | None = None
    location: address_serialize.LocationBodyModelV2 | address_serialize.LocationOnlyOnVenueBodyModelV2 | None = (
        pydantic_v2.Field(default=None, discriminator="isVenueLocation")
    )

    @pydantic_v2.model_validator(mode="after")
    def validate_location_comment(self) -> typing.Self:
        if self.locationType != models.CollectiveLocationType.TO_BE_DEFINED and self.locationComment is not None:
            raise_error_from_location(
                None, loc="locationComment", msg="locationComment n'est pas autorisé pour cette valeur de locationType"
            )

        return self

    @pydantic_v2.model_validator(mode="after")
    def validate_location(self) -> typing.Self:
        if (
            self.locationType
            in (
                models.CollectiveLocationType.SCHOOL,
                models.CollectiveLocationType.TO_BE_DEFINED,
            )
            and self.location is not None
        ):
            raise_error_from_location(
                None, loc="location", msg="location n'est pas autorisé pour cette valeur de locationType"
            )

        if self.locationType == models.CollectiveLocationType.ADDRESS and self.location is None:
            raise_error_from_location(None, loc="location", msg="location est requis pour cette valeur de locationType")

        return self


def validate_intervention_area_with_location_v2(
    intervention_area: list[str] | None, location: CollectiveOfferLocationModelV2
) -> None:
    if intervention_area:
        if location.locationType == models.CollectiveLocationType.ADDRESS:
            raise_error_from_location(
                None, loc="interventionArea", msg="interventionArea doit être vide pour cette valeur de locationType"
            )

        if any(area not in constants.ALL_INTERVENTION_AREA for area in intervention_area):
            raise_error_from_location(
                None, loc="interventionArea", msg="interventionArea doit contenir des départements valides"
            )

    elif location.locationType in (models.CollectiveLocationType.TO_BE_DEFINED, models.CollectiveLocationType.SCHOOL):
        raise_error_from_location(
            None, loc="interventionArea", msg="interventionArea ne peut pas être vide pour cette valeur de locationType"
        )


class PostCollectiveOfferBodyModel(HttpBodyModel):
    venue_id: int
    name: str = pydantic_v2.Field(max_length=constants.MAX_COLLECTIVE_NAME_LENGTH)
    booking_emails: list[pydantic_v2.EmailStr] = pydantic_v2.Field(min_length=1)
    description: str = pydantic_v2.Field(max_length=constants.MAX_COLLECTIVE_DESCRIPTION_LENGTH)
    domains: list[int] = pydantic_v2.Field(min_length=1)
    duration_minutes: int | None = None
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool
    students: list[models.StudentLevels] = pydantic_v2.Field(min_length=1)
    location: CollectiveOfferLocationModelV2
    contact_email: pydantic_v2.EmailStr | None = None
    contact_phone: str | None = None
    intervention_area: list[str] | None
    template_id: int | None = None
    nationalProgramId: int | None = None
    formats: list[EacFormat] = pydantic_v2.Field(min_length=1)

    @pydantic_v2.field_validator("students")
    @classmethod
    def validate_students(cls, students: list[models.StudentLevels]) -> list[models.StudentLevels]:
        try:
            # TODO (jcicurel-pass, 2026-02-04): refactor validate_students to raise correct error
            # when all models using it are migrated to v2
            shared_offers.validate_students(students)
        except ValueError as ex:
            raise PydanticError(str(ex))

        return students

    @pydantic_v2.model_validator(mode="after")
    def validate_intervention_area(self) -> typing.Self:
        validate_intervention_area_with_location_v2(self.intervention_area, self.location)

        return self


class PostCollectiveOfferTemplateBodyModel(PostCollectiveOfferBodyModel):
    price_detail: str | None = pydantic_v2.Field(default=None, max_length=constants.MAX_COLLECTIVE_PRICE_DETAILS_LENGTH)
    contact_url: pydantic_v2.AnyHttpUrl | None = None
    contact_form: models.OfferContactFormEnum | None = None
    dates: PostDateRangeModel | None = None


class PatchCollectiveOfferBodyModel(BaseModel, AccessibilityComplianceMixin):
    bookingEmails: list[EmailStr] | None
    description: str | None
    name: str | None
    students: list[models.StudentLevels] | None
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
    def validate_students(cls, students: list[str] | None) -> list[models.StudentLevels] | None:
        if not students:
            return None
        return shared_offers.validate_students(students)

    @validator("name")
    def validate_name(cls, name: str | None) -> str | None:
        assert name is not None and name.strip() != ""
        validation.check_collective_offer_name_length_is_valid(name)
        return name

    @validator("description")
    def validate_description(cls, description: str | None) -> str | None:
        if description is None:
            raise ValueError("Description cannot be NULL.")
        validation.check_collective_offer_description_length_is_valid(description)
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
    contactForm: models.OfferContactFormEnum | None

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


class PatchCollectiveOfferActiveStatusBodyModel(HttpBodyModel):
    is_active: bool
    ids: list[int]


class PatchCollectiveOfferArchiveBodyModel(HttpBodyModel):
    ids: list[int]


class PatchCollectiveOfferEducationalInstitution(HttpBodyModel):
    educational_institution_id: int
    teacher_email: str | None = None


class AttachImageFormModel(HttpBodyModel):
    # thumb comes from request.files, it is inserted in the model when validated by spectree
    # but it is not present in the model received by the route itself
    thumb: BaseFile | None = None
    credit: str
    cropping_rect_x: float
    cropping_rect_y: float
    cropping_rect_height: float
    cropping_rect_width: float


class AttachImageResponseModel(HttpBodyModel):
    image_url: str
