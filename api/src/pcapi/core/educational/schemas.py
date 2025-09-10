import dataclasses
import datetime
import decimal
import enum
import typing
from typing import Any

from pydantic.v1 import AnyHttpUrl
from pydantic.v1 import ConstrainedStr
from pydantic.v1 import EmailStr
from pydantic.v1 import Field
from pydantic.v1 import PositiveInt
from pydantic.v1 import root_validator
from pydantic.v1 import validator
from pydantic.v1.fields import ModelField

from pcapi import settings
from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.shared import schemas as shared_schemas
from pcapi.core.shared.schemas import AccessibilityComplianceMixin
from pcapi.models import api_errors
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.utils import date as date_utils


class AdageBaseResponseModel(BaseModel):
    class Config:
        json_encoders = {datetime.datetime: date_utils.format_into_utc_date}


class AdageCulturalPartner(BaseModel):
    id: int
    venueId: int | None
    siret: str | None
    regionId: int | None
    academieId: str | None
    statutId: int | None
    labelId: int | None
    typeId: int | None
    communeId: str | None
    libelle: str
    adresse: str | None
    siteWeb: str | None
    latitude: float | None
    longitude: float | None
    statutLibelle: str | None
    labelLibelle: str | None
    typeIcone: str | None
    typeLibelle: str | None
    communeLibelle: str | None
    communeDepartement: str | None
    academieLibelle: str | None
    regionLibelle: str | None
    domaines: str | None
    actif: int | None
    dateModification: datetime.datetime
    synchroPass: int | None
    domaineIds: str | None


class AdageCulturalPartners(BaseModel):
    partners: list[AdageCulturalPartner]


class Contact(AdageBaseResponseModel):
    email: str | None
    phone: str | None


class Redactor(AdageBaseResponseModel):
    email: str
    redactorFirstName: str | None
    redactorLastName: str | None
    redactorCivility: str | None

    class Config:
        alias_generator = to_camel


class EducationalBookingResponse(AdageBaseResponseModel):
    accessibility: str = Field(description="Accessibility of the offer")
    address: str = Field(description="Adresse of event")
    startDatetime: datetime.datetime = Field(description="Start date of event")
    endDatetime: datetime.datetime = Field(description="End date of event")
    cancellationDate: datetime.datetime | None = Field(description="Date of cancellation if prebooking is cancelled")
    cancellationLimitDate: datetime.datetime | None = Field(description="Limit date to cancel the prebooking")
    confirmationDate: datetime.datetime | None = Field(description="Date of confirmation if prebooking is confirmed")
    confirmationLimitDate: datetime.datetime = Field(description="Limit date to confirm the prebooking")
    contact: Contact = Field(description="Contact of the prebooking")
    creationDate: datetime.datetime
    description: str | None = Field(description="Offer description")
    durationMinutes: int | None = Field(description="Offer's duration in minutes")
    expirationDate: datetime.datetime | None = Field(description="Expiration date after which booking is cancelled")
    id: int = Field(description="pass Culture's prebooking id")
    isDigital: bool = Field(description="If true the event is accessed digitally")
    venueName: str = Field(description="Name of cultural venue proposing the event")
    name: str = Field(description="Name of event")
    numberOfTickets: int | None = Field(description="Number of tickets")
    price: decimal.Decimal
    quantity: int = Field(description="Number of place prebooked")
    redactor: Redactor
    UAICode: str = Field(description="Educational institution UAI code")
    yearId: int = Field(description="Shared year id")
    status: models.EducationalBookingStatus | models.CollectiveBookingStatus
    cancellationReason: models.CollectiveBookingCancellationReasons | None = Field(
        description="Reason when a prebooking order is cancelled"
    )
    participants: list[str] = Field(description="List of class levels which can participate")
    priceDetail: str | None = Field(description="Offer's stock price detail")
    venueTimezone: str
    totalAmount: decimal.Decimal = Field(description="Total price of the prebooking")
    url: str | None = Field(description="Url to access the offer")
    withdrawalDetails: str | None
    domain_ids: list[int]
    domain_labels: list[str]
    interventionArea: list[str]
    imageCredit: str | None = Field(description="Credit for the source image")
    imageUrl: str | None = Field(description="Url for offer image")
    venueId: int
    offererName: str
    formats: list[EacFormat]

    class Config:
        title = "Prebooking detailed response"
        alias_generator = to_camel
        allow_population_by_field_name = True


class EducationalBookingEdition(EducationalBookingResponse):
    updatedFields: list[str] = Field(description="List of fields updated")


class AdageReimbursementNotification(EducationalBookingResponse):
    reimbursementReason: str
    reimbursedValue: decimal.Decimal
    reimbursementDetails: str


class RedactorInformation(BaseModel):
    civility: str | None
    lastname: str | None
    firstname: str | None
    email: str
    uai: str


class MergeInstitutionPrebookingsQueryModel(AdageBaseResponseModel):
    source_uai: str
    destination_uai: str
    bookings_ids: list[int]


class GetEducationalBookingsRequest(BaseModel):
    redactorEmail: str | None = Field(description="Email of querying redactor")

    class Config:
        title = "Prebookings query filters"


class EducationalBookingsResponse(AdageBaseResponseModel):
    prebookings: list[EducationalBookingResponse]

    class Config:
        title = "List of prebookings"


class EducationalBookingPerYearResponse(AdageBaseResponseModel):
    id: int
    UAICode: str
    status: models.EducationalBookingStatus | models.CollectiveBookingStatus
    cancellationReason: models.CollectiveBookingCancellationReasons | None
    confirmationLimitDate: datetime.datetime
    totalAmount: decimal.Decimal
    startDatetime: datetime.datetime
    endDatetime: datetime.datetime
    venueTimezone: str
    name: str
    redactorEmail: str
    domainIds: list[int]
    domainLabels: list[str]
    venueId: int | None
    venueName: str | None
    offererName: str | None
    formats: typing.Sequence[EacFormat]

    class Config:
        use_enum_values = True


class EducationalBookingsPerYearResponse(AdageBaseResponseModel):
    bookings: list[EducationalBookingPerYearResponse]


class GetAllBookingsPerYearQueryModel(BaseModel):
    page: PositiveInt | None
    per_page: PositiveInt | None


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class CollectiveOffersFilter:
    user_id: int
    offerer_id: int | None = None
    statuses: list[models.CollectiveOfferDisplayedStatus] | None = None
    venue_id: int | None = None
    provider_id: int | None = None
    name_keywords: str | None = None
    period_beginning_date: datetime.date | None = None
    period_ending_date: datetime.date | None = None
    formats: list[EacFormat] | None = None
    location_type: models.CollectiveLocationType | None = None
    offerer_address_id: int | None = None


def validate_start_datetime(
    start_datetime: datetime.datetime, values: dict[str, Any], field: ModelField
) -> datetime.datetime:
    # we need a datetime withdatetime.datetime.timezone information which is not provided bydatetime.datetime.utcnow.
    if start_datetime and start_datetime < datetime.datetime.now(datetime.timezone.utc):
        raise ValueError("L'évènement ne peut commencer dans le passé.")
    return start_datetime


def start_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_start_datetime)


def validate_end_datetime(
    end_datetime: datetime.datetime, values: dict[str, Any], field: ModelField
) -> datetime.datetime:
    # we need a datetime withdatetime.datetime.timezone information which is not provided bydatetime.datetime.utcnow.
    start_datetime = values.get("start_datetime")
    if end_datetime and end_datetime < datetime.datetime.now(datetime.timezone.utc):
        raise ValueError("L'évènement ne peut se terminer dans le passé.")
    if start_datetime and end_datetime < start_datetime:
        raise ValueError("La date de fin de l'évènement ne peut précéder la date de début.")
    return end_datetime


def end_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_end_datetime)


def validate_booking_limit_datetime(
    booking_limit_datetime: datetime.datetime | None, values: dict[str, Any]
) -> datetime.datetime | None:
    if booking_limit_datetime and values.get("start_datetime") and booking_limit_datetime > values["start_datetime"]:
        raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
    return booking_limit_datetime


def booking_limit_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_booking_limit_datetime)


def validate_price(price: float | None) -> float:
    if price is None:
        raise ValueError("Le prix ne peut pas être nul.")
    if price < 0:
        raise ValueError("Le prix ne peut pas être négatif.")
    if price > settings.EAC_OFFER_PRICE_LIMIT:
        raise ValueError("Le prix est trop élevé.")
    return price


def price_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_price)


def validate_number_of_tickets(number_of_tickets: int | None) -> int:
    if number_of_tickets is None:
        raise ValueError("Le nombre de places ne peut pas être nul.")
    if number_of_tickets < 0:
        raise ValueError("Le nombre de places ne peut pas être négatif.")
    if number_of_tickets > settings.EAC_NUMBER_OF_TICKETS_LIMIT:
        raise ValueError("Le nombre de places est trop élevé.")
    return number_of_tickets


def number_of_tickets_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_number_of_tickets)


def price_detail_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_price_detail)


def validate_price_detail(educational_price_detail: str | None) -> str | None:
    if educational_price_detail and len(educational_price_detail) > 1000:
        raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
    return educational_price_detail


class CollectiveStockCreationBodyModel(BaseModel):
    offer_id: int
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime | None
    booking_limit_datetime: datetime.datetime | None
    total_price: decimal.Decimal
    number_of_tickets: int
    educational_price_detail: str | None

    _validate_number_of_tickets = number_of_tickets_validator("number_of_tickets")
    _validate_total_price = price_validator("total_price")
    _validate_start_datetime = start_datetime_validator("start_datetime")
    _validate_end_datetime = end_datetime_validator("end_datetime")
    _validate_booking_limit_datetime = booking_limit_datetime_validator("booking_limit_datetime")
    _validate_educational_price_detail = price_detail_validator("educational_price_detail")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOfferType(enum.Enum):
    offer = "offer"
    template = "template"


class CollectiveOfferLocationModel(BaseModel):
    locationType: educational_models.CollectiveLocationType
    locationComment: str | None
    address: offerers_schemas.AddressBodyModel | None

    @validator("locationComment")
    def validate_location_comment(cls, location_comment: str | None, values: dict) -> str | None:
        location_type = values.get("locationType")
        if location_type != educational_models.CollectiveLocationType.TO_BE_DEFINED and location_comment is not None:
            raise ValueError("locationComment is not allowed for the provided locationType")
        return location_comment

    @validator("address")
    def validate_address(
        cls, address: offerers_schemas.AddressBodyModel | None, values: dict
    ) -> offerers_schemas.AddressBodyModel | None:
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


def validate_venue_id(venue_id: int | str | None) -> int | None:
    # TODO(jeremieb): remove this validator once there is no empty
    # string stored as a venueId
    if not venue_id:
        return None
    return int(venue_id)  # should not be needed but it makes mypy happy


class CollectiveOfferVenueBodyModel(BaseModel):
    addressType: educational_models.OfferAddressType
    otherAddress: str
    venueId: int | None

    _validated_venue_id = validator("venueId", pre=True, allow_reuse=True)(validate_venue_id)

    class Config:
        alias_generator = to_camel
        extra = "forbid"


def is_intervention_area_valid(
    intervention_area: list[str] | None,
    offer_venue: CollectiveOfferVenueBodyModel | None,
) -> bool:
    if intervention_area is None:
        return False

    if offer_venue is not None and offer_venue.addressType == educational_models.OfferAddressType.OFFERER_VENUE:
        return True

    if len(intervention_area) == 0:
        return False

    return True


def validate_intervention_area_with_location(
    intervention_area: list[str] | None,
    location: CollectiveOfferLocationModel,
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


def check_collective_offer_name_length_is_valid(offer_name: str) -> None:
    if len(offer_name) > models.MAX_COLLECTIVE_NAME_LENGTH:
        raise api_errors.ApiErrors(
            errors={
                "name": [f"Le titre de l’offre doit faire au maximum {models.MAX_COLLECTIVE_NAME_LENGTH} caractères."]
            }
        )


def check_collective_offer_description_length_is_valid(offer_description: str) -> None:
    if len(offer_description) > models.MAX_COLLECTIVE_DESCRIPTION_LENGTH:
        raise api_errors.ApiErrors(
            {
                "description": [
                    f"La description de l’offre doit faire au maximum {models.MAX_COLLECTIVE_DESCRIPTION_LENGTH} caractères."
                ]
            }
        )


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
    # offerVenue will be replaced with location, for now we accept one or the other (but not both)
    offer_venue: CollectiveOfferVenueBodyModel | None
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
        check_collective_offer_name_length_is_valid(name)
        return name

    @validator("description")
    def validate_description(cls, description: str) -> str:
        check_collective_offer_description_length_is_valid(description)
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

    @validator("offer_venue")
    def validate_offer_venue(
        cls, offer_venue: CollectiveOfferVenueBodyModel | None
    ) -> CollectiveOfferVenueBodyModel | None:
        if offer_venue is not None:
            raise ValueError("Cannot receive offerVenue, use location instead")

        return offer_venue

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class DateRangeModel(BaseModel):
    start: datetime.datetime
    end: datetime.datetime

    @validator("start")
    def validate_start(cls, start: datetime.datetime) -> datetime.datetime:
        return date_utils.without_timezone(start)

    @validator("end")
    def validate_end(cls, end: datetime.datetime) -> datetime.datetime:
        return date_utils.without_timezone(end)

    @root_validator(skip_on_failure=True)
    def validate_end_before_start(cls, values: dict) -> dict:
        if values["start"] > values["end"]:
            raise ValueError("end before start")

        return values


class DateRangeOnCreateModel(DateRangeModel):
    @validator("start")
    def validate_start(cls, start: datetime.datetime) -> datetime.datetime:
        start = super().validate_start(start)

        if start.date() < datetime.date.today():
            raise ValueError("start date can't be passed")
        return start


class PriceDetail(ConstrainedStr):
    max_length: int = 1_000


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
    # offerVenue will be replaced with location, for now we accept one or the other (but not both)
    offerVenue: CollectiveOfferVenueBodyModel | None
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
        check_collective_offer_name_length_is_valid(name)
        return name

    @validator("description")
    def validate_description(cls, description: str | None) -> str | None:
        if description is None:
            raise ValueError("Description cannot be NULL.")
        check_collective_offer_description_length_is_valid(description)
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

    @validator("offerVenue")
    def validate_offer_venue(
        cls, offer_venue: CollectiveOfferVenueBodyModel | None
    ) -> CollectiveOfferVenueBodyModel | None:
        if offer_venue is not None:
            raise ValueError("Cannot receive offerVenue, use location instead")

        return offer_venue

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


class AdageCulturalPartnerResponseModel(BaseModel):
    id: int
    statutId: int | None
    siteWeb: str | None
    domaineIds: list[int]

    @validator("domaineIds", pre=True)
    @classmethod
    def transform_domaine_ids(cls, domaine_ids: str | list[int] | None) -> list[int]:
        if not domaine_ids:
            return []

        if isinstance(domaine_ids, list):
            return domaine_ids

        split_domaine_ids = domaine_ids.split(",")
        ids = []
        for domaine_id in split_domaine_ids:
            if not domaine_id.isdigit():
                raise ValueError("Domaine id must be an integer")
            ids.append(int(domaine_id))

        return ids

    class Config:
        orm_mode = True


class GetCollectiveOfferLocationModel(BaseModel):
    locationType: models.CollectiveLocationType
    locationComment: str | None
    address: shared_schemas.AddressResponseIsLinkedToVenueModel | None
