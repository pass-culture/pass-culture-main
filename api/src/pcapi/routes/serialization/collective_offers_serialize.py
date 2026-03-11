import typing
from datetime import date
from datetime import datetime

import pydantic as pydantic_v2
from spectree.models import BaseFile

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import constants
from pcapi.core.educational import models
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.routes.serialization import address_serialize
from pcapi.routes.serialization import collective_history_serialize
from pcapi.routes.serialization import educational_institutions
from pcapi.routes.serialization import national_programs
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.utils import raise_error_from_location
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.serialization import utils
from pcapi.serialization.exceptions import PydanticError


### GET all collective offers models
class ListCollectiveOffersQueryModel(HttpQueryParamsModel):
    name: str | None = None
    offerer_id: int | None = None
    status: typing.Annotated[list[models.CollectiveOfferDisplayedStatus] | None, utils.ArgsAsListBeforeValidator] = None
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


class CollectiveOfferStockResponseModel(HttpBodyModel):
    bookingLimitDatetime: datetime
    price: float
    numberOfTickets: int


class DatesModel(HttpBodyModel):
    start: datetime
    end: datetime


class GetCollectiveOfferLocationModelV2(HttpBodyModel):
    locationType: models.CollectiveLocationType
    locationComment: str | None
    location: address_serialize.LocationResponseModelV2 | None

    @classmethod
    def build(cls, offer: models.CollectiveOffer | models.CollectiveOfferTemplate) -> typing.Self:
        location = None
        oa = offer.offererAddress
        venue = offer.venue

        if oa is not None:
            is_venue_location = venue.offererAddress.addressId == oa.addressId and (
                oa.label is None or oa.label == venue.publicName
            )

            location = address_serialize.LocationResponseModelV2.build(
                offerer_address=oa,
                label=venue.publicName if is_venue_location else oa.label,
                is_venue_location=is_venue_location,
            )

        return cls(locationType=offer.locationType, locationComment=offer.locationComment, location=location)


class CollectiveOfferResponseModel(HttpBodyModel):
    id: int
    name: str
    venue: venues_serialize.ListOffersVenueResponseModelV2
    displayedStatus: models.CollectiveOfferDisplayedStatus
    imageUrl: str | None
    location: GetCollectiveOfferLocationModelV2
    dates: DatesModel | None
    # collective offer specific fields
    allowedActions: list[models.CollectiveOfferAllowedAction]
    stock: CollectiveOfferStockResponseModel | None
    educationalInstitution: educational_institutions.EducationalInstitutionResponseModel | None

    @classmethod
    def build(cls, offer: models.CollectiveOffer) -> typing.Self:
        stock = offer.collectiveStock
        serialized_stock = CollectiveOfferStockResponseModel.model_validate(stock) if stock is not None else None

        start, end = offer.start, offer.end
        if start is not None and end is not None:
            dates = DatesModel(start=start, end=end)
        else:
            dates = None

        return cls(
            id=offer.id,
            name=offer.name,
            venue=venues_serialize.ListOffersVenueResponseModelV2.build(offer.venue),
            displayedStatus=offer.displayedStatus,
            allowedActions=offer.allowedActions,
            imageUrl=offer.imageUrl,
            location=GetCollectiveOfferLocationModelV2.build(offer),
            stock=serialized_stock,
            educationalInstitution=offer.institution,
            dates=dates,
        )


class ListCollectiveOffersResponseModel(pydantic_v2.RootModel):
    root: list[CollectiveOfferResponseModel]


class CollectiveOfferTemplateResponseModel(HttpBodyModel):
    id: int
    name: str
    venue: venues_serialize.ListOffersVenueResponseModelV2
    displayedStatus: models.CollectiveOfferDisplayedStatus
    imageUrl: str | None
    location: GetCollectiveOfferLocationModelV2
    dates: DatesModel | None
    # collective offer template specific fields
    allowedActions: list[models.CollectiveOfferTemplateAllowedAction]

    @classmethod
    def build(cls, offer: models.CollectiveOfferTemplate) -> "CollectiveOfferTemplateResponseModel":
        start, end = offer.start, offer.end
        if start is not None and end is not None:
            dates = DatesModel(start=start, end=end)
        else:
            dates = None

        return cls(
            id=offer.id,
            name=offer.name,
            venue=venues_serialize.ListOffersVenueResponseModelV2.build(offer.venue),
            displayedStatus=offer.displayedStatus,
            allowedActions=offer.allowedActions,
            imageUrl=offer.imageUrl,
            dates=dates,
            location=GetCollectiveOfferLocationModelV2.build(offer),
        )


class ListCollectiveOfferTemplatesResponseModel(pydantic_v2.RootModel):
    root: list[CollectiveOfferTemplateResponseModel]


### GET one collective offer models
class OfferDomain(HttpBodyModel):
    id: int
    name: str


class GetCollectiveOfferManagingOffererResponseModel(HttpBodyModel):
    id: int
    name: str
    siren: str


class GetCollectiveOfferVenueResponseModel(HttpBodyModel):
    departementCode: str
    id: int
    managingOfferer: GetCollectiveOfferManagingOffererResponseModel
    name: str
    publicName: str
    bannerUrl: str | None = pydantic_v2.Field(alias="imgUrl")

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> typing.Self:
        return cls(
            departementCode=venue.offererAddress.address.departmentCode,
            id=venue.id,
            managingOfferer=venue.managingOfferer,
            name=venue.name,
            publicName=venue.publicName,
            bannerUrl=venue.bannerUrl,
        )


class GetCollectiveOfferBaseResponseModel(HttpBodyModel):
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None
    bookingEmails: list[str]
    dateCreated: datetime
    description: str
    durationMinutes: int | None
    students: list[models.StudentLevels]
    location: GetCollectiveOfferLocationModelV2
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
    nationalProgram: national_programs.NationalProgramResponseModel | None
    formats: list[EacFormat]
    dates: DatesModel | None


class GetCollectiveOfferTemplateResponseModel(GetCollectiveOfferBaseResponseModel):
    priceDetail: str | None = pydantic_v2.Field(alias="educationalPriceDetail")
    isTemplate: bool = True
    contactUrl: str | None
    contactForm: models.OfferContactFormEnum | None
    allowedActions: list[models.CollectiveOfferTemplateAllowedAction]

    @classmethod
    def build(cls, offer: models.CollectiveOfferTemplate) -> typing.Self:
        national_program = (
            national_programs.NationalProgramResponseModel.model_validate(offer.nationalProgram)
            if offer.nationalProgram
            else None
        )

        if offer.start and offer.end:
            dates = DatesModel(start=offer.start, end=offer.end)
        else:
            dates = None

        return cls(
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
            bookingEmails=offer.bookingEmails,
            dateCreated=offer.dateCreated,
            description=offer.description,
            durationMinutes=offer.durationMinutes,
            students=offer.students,
            location=GetCollectiveOfferLocationModelV2.build(offer),
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            id=offer.id,
            name=offer.name,
            venue=GetCollectiveOfferVenueResponseModel.build(offer.venue),
            displayedStatus=offer.displayedStatus,
            domains=[OfferDomain.model_validate(domain) for domain in offer.domains],
            interventionArea=offer.interventionArea,
            imageCredit=offer.imageCredit,
            imageUrl=offer.imageUrl,
            nationalProgram=national_program,
            formats=offer.formats,
            dates=dates,
            priceDetail=offer.priceDetail,
            isTemplate=True,
            contactUrl=offer.contactUrl,
            contactForm=offer.contactForm,
            allowedActions=offer.allowedActions,
        )


class GetCollectiveOfferCollectiveStockResponseModel(HttpBodyModel):
    id: int
    startDatetime: datetime
    endDatetime: datetime
    bookingLimitDatetime: datetime
    price: float
    numberOfTickets: int
    priceDetail: str | None = pydantic_v2.Field(alias="educationalPriceDetail")


class EducationalRedactorResponseModel(HttpBodyModel):
    email: str
    firstName: str | None
    lastName: str | None
    civility: str | None


class GetCollectiveOfferBookingResponseModel(HttpBodyModel):
    id: int
    dateCreated: datetime
    status: models.CollectiveBookingStatus
    educationalRedactor: EducationalRedactorResponseModel
    cancellationLimitDate: datetime
    cancellationReason: models.CollectiveBookingCancellationReasons | None
    confirmationLimitDate: datetime


class GetCollectiveOfferProviderResponseModel(HttpBodyModel):
    name: str


class GetCollectiveOfferResponseModel(GetCollectiveOfferBaseResponseModel):
    collectiveStock: GetCollectiveOfferCollectiveStockResponseModel | None
    lastBooking: GetCollectiveOfferBookingResponseModel | None = pydantic_v2.Field(alias="booking")
    institution: educational_institutions.EducationalInstitutionResponseModel | None
    templateId: int | None
    teacher: EducationalRedactorResponseModel | None
    isPublicApi: bool
    provider: GetCollectiveOfferProviderResponseModel | None
    isTemplate: bool = False
    allowedActions: list[models.CollectiveOfferAllowedAction]
    history: collective_history_serialize.CollectiveOfferHistory

    @classmethod
    def build(cls, offer: models.CollectiveOffer) -> typing.Self:
        national_program = (
            national_programs.NationalProgramResponseModel.model_validate(offer.nationalProgram)
            if offer.nationalProgram
            else None
        )

        if offer.start and offer.end:
            dates = DatesModel(start=offer.start, end=offer.end)
        else:
            dates = None

        collective_stock = (
            GetCollectiveOfferCollectiveStockResponseModel.model_validate(offer.collectiveStock)
            if offer.collectiveStock
            else None
        )

        last_booking = (
            GetCollectiveOfferBookingResponseModel.model_validate(offer.lastBooking) if offer.lastBooking else None
        )

        institution = (
            educational_institutions.EducationalInstitutionResponseModel.model_validate(offer.institution)
            if offer.institution
            else None
        )

        teacher = EducationalRedactorResponseModel.model_validate(offer.teacher) if offer.teacher else None

        provider = GetCollectiveOfferProviderResponseModel.model_validate(offer.provider) if offer.provider else None

        return cls(
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
            bookingEmails=offer.bookingEmails,
            dateCreated=offer.dateCreated,
            description=offer.description,
            durationMinutes=offer.durationMinutes,
            students=offer.students,
            location=GetCollectiveOfferLocationModelV2.build(offer),
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            id=offer.id,
            name=offer.name,
            venue=GetCollectiveOfferVenueResponseModel.build(offer.venue),
            displayedStatus=offer.displayedStatus,
            domains=[OfferDomain.model_validate(domain) for domain in offer.domains],
            interventionArea=offer.interventionArea,
            imageCredit=offer.imageCredit,
            imageUrl=offer.imageUrl,
            nationalProgram=national_program,
            formats=offer.formats,
            dates=dates,
            collectiveStock=collective_stock,
            lastBooking=last_booking,
            institution=institution,
            templateId=offer.templateId,
            teacher=teacher,
            isPublicApi=offer.isPublicApi,
            provider=provider,
            isTemplate=False,
            allowedActions=offer.allowedActions,
            history=collective_history_serialize.get_collective_offer_history(offer),
        )


### GET collective offers models for home
class CollectiveStockHomeResponseModel(HttpBodyModel):
    startDatetime: datetime
    endDatetime: datetime
    bookingLimitDatetime: datetime
    numberOfTickets: int


class ListCollectiveOffersHomeQueryModel(HttpQueryParamsModel):
    venue_id: int


class CollectiveOfferHomeResponseModel(HttpBodyModel):
    id: int
    name: str
    displayedStatus: models.CollectiveOfferDisplayedStatus
    imageUrl: str | None
    allowedActions: list[models.CollectiveOfferAllowedAction]
    collectiveStock: CollectiveStockHomeResponseModel | None


class ListCollectiveOffersHomeResponseModel(HttpBodyModel):
    has_offers: bool
    offers: list[CollectiveOfferHomeResponseModel]


### POST collective offer models
class PatchDateRangeModel(HttpBodyModel):
    start: datetime
    end: datetime

    @pydantic_v2.field_validator("start", "end")
    @classmethod
    def remove_timezone(cls, date_time: datetime) -> datetime:
        return utils.without_timezone(date_time)

    @pydantic_v2.model_validator(mode="after")
    def validate_end_before_start(self) -> typing.Self:
        if self.start > self.end:
            raise PydanticError("La date de début doit être avant la date de fin")

        return self


class PostDateRangeModel(PatchDateRangeModel):
    @pydantic_v2.field_validator("start")
    @classmethod
    def validate_start(cls, start: datetime) -> datetime:
        if start.date() < date.today():
            raise PydanticError("La date de début ne peut pas être dans le passé")

        return start


class CollectiveOfferLocationModel(HttpBodyModel):
    location_type: models.CollectiveLocationType
    location_comment: str | None = None
    location: address_serialize.LocationBodyModelV2 | address_serialize.LocationOnlyOnVenueBodyModelV2 | None = (
        pydantic_v2.Field(default=None, discriminator="isVenueLocation")
    )

    @pydantic_v2.model_validator(mode="after")
    def validate_location_comment(self) -> typing.Self:
        if self.location_type != models.CollectiveLocationType.TO_BE_DEFINED and self.location_comment is not None:
            raise_error_from_location(
                None, loc="locationComment", msg="locationComment n'est pas autorisé pour cette valeur de locationType"
            )

        return self

    @pydantic_v2.model_validator(mode="after")
    def validate_location(self) -> typing.Self:
        if (
            self.location_type
            in (
                models.CollectiveLocationType.SCHOOL,
                models.CollectiveLocationType.TO_BE_DEFINED,
            )
            and self.location is not None
        ):
            raise_error_from_location(
                None, loc="location", msg="location n'est pas autorisé pour cette valeur de locationType"
            )

        if self.location_type == models.CollectiveLocationType.ADDRESS and self.location is None:
            raise_error_from_location(None, loc="location", msg="location est requis pour cette valeur de locationType")

        return self


def validate_intervention_area(value: list[str] | None, info: pydantic_v2.ValidationInfo) -> list[str] | None:
    location: CollectiveOfferLocationModel | None = info.data.get("location")

    if location is None:
        return value

    if value:
        if location.location_type == models.CollectiveLocationType.ADDRESS:
            raise PydanticError("interventionArea doit être vide pour cette valeur de locationType")

        if any(area not in constants.ALL_INTERVENTION_AREA for area in value):
            raise PydanticError("interventionArea doit contenir des départements valides")

    elif location.location_type in (
        models.CollectiveLocationType.TO_BE_DEFINED,
        models.CollectiveLocationType.SCHOOL,
    ):
        raise PydanticError("interventionArea ne peut pas être vide pour cette valeur de locationType")

    return value


def validate_students(students: list[models.StudentLevels]) -> list[models.StudentLevels]:
    try:
        # TODO (jcicurel-pass, 2026-02-04): refactor validate_students to raise correct error
        # when all models using it are migrated to v2
        shared_offers.validate_students(students)
    except ValueError as ex:
        raise PydanticError(str(ex))

    return students


class PostCollectiveOfferBodyModel(HttpBodyModel):
    venue_id: int
    name: str = pydantic_v2.Field(min_length=1, max_length=constants.MAX_COLLECTIVE_NAME_LENGTH)
    booking_emails: list[pydantic_v2.EmailStr] = pydantic_v2.Field(min_length=1)
    description: str = pydantic_v2.Field(max_length=constants.MAX_COLLECTIVE_DESCRIPTION_LENGTH)
    domains: list[int] = pydantic_v2.Field(min_length=1)
    duration_minutes: int | None = None
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool
    students: typing.Annotated[list[models.StudentLevels], pydantic_v2.AfterValidator(validate_students)] = (
        pydantic_v2.Field(min_length=1)
    )
    location: CollectiveOfferLocationModel
    contact_email: pydantic_v2.EmailStr | None = None
    contact_phone: str | None = None
    intervention_area: typing.Annotated[list[str] | None, pydantic_v2.AfterValidator(validate_intervention_area)]
    template_id: int | None = None
    national_program_id: int | None = None
    formats: list[EacFormat] = pydantic_v2.Field(min_length=1)


class PostCollectiveOfferTemplateBodyModel(PostCollectiveOfferBodyModel):
    price_detail: str | None = pydantic_v2.Field(default=None, max_length=constants.MAX_COLLECTIVE_PRICE_DETAILS_LENGTH)
    contact_url: pydantic_v2.AnyHttpUrl | None = None
    contact_form: models.OfferContactFormEnum | None = None
    dates: PostDateRangeModel | None = None


class CollectiveOfferResponseIdModel(HttpBodyModel):
    id: int


### PATCH collective offer models
class PatchCollectiveOfferBodyModel(HttpBodyModel):
    audio_disability_compliant: bool | None = None
    mental_disability_compliant: bool | None = None
    motor_disability_compliant: bool | None = None
    visual_disability_compliant: bool | None = None
    booking_emails: list[pydantic_v2.EmailStr] | None = pydantic_v2.Field(min_length=1, default=None)
    description: str | None = pydantic_v2.Field(max_length=constants.MAX_COLLECTIVE_DESCRIPTION_LENGTH, default=None)
    name: str | None = pydantic_v2.Field(min_length=1, max_length=constants.MAX_COLLECTIVE_NAME_LENGTH, default=None)
    students: typing.Annotated[list[models.StudentLevels] | None, pydantic_v2.AfterValidator(validate_students)] = (
        pydantic_v2.Field(min_length=1, default=None)
    )
    location: CollectiveOfferLocationModel | None = None
    contact_email: pydantic_v2.EmailStr | None = None
    contact_phone: str | None = None
    duration_minutes: int | None = None
    domains: list[int] | None = pydantic_v2.Field(min_length=1, default=None)
    intervention_area: typing.Annotated[list[str] | None, pydantic_v2.AfterValidator(validate_intervention_area)] = None
    venue_id: int | None = None
    national_program_id: int | None = None
    formats: list[EacFormat] | None = pydantic_v2.Field(min_length=1, default=None)

    NON_NULLABLE_FIELDS: typing.ClassVar = (
        "booking_emails",
        "description",
        "name",
        "students",
        "location",
        "domains",
        "intervention_area",
        "venue_id",
        "formats",
    )

    @pydantic_v2.field_validator(*NON_NULLABLE_FIELDS, mode="before")
    @classmethod
    def validate_not_none(cls, value: typing.Any) -> typing.Any:
        if value is None:
            raise PydanticError("Ce champ ne peut pas être null")

        return value


class PatchCollectiveOfferTemplateBodyModel(PatchCollectiveOfferBodyModel):
    price_detail: str | None = pydantic_v2.Field(max_length=constants.MAX_COLLECTIVE_PRICE_DETAILS_LENGTH, default=None)
    dates: PatchDateRangeModel | None = None
    contact_url: str | None = None
    contact_form: models.OfferContactFormEnum | None = None

    @pydantic_v2.model_validator(mode="after")
    def validate_contact_fields(self) -> typing.Self:
        if self.contact_url is not None and self.contact_form is not None:
            raise PydanticError("contactUrl et contactForm ne peuvent pas être remplis en même temps")

        return self


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
