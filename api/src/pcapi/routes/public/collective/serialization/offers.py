import decimal
import typing
from datetime import datetime
from datetime import timezone

from pydantic.v1 import root_validator
from pydantic.v1 import validator

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import validation as educational_validation
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveLocationType
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.educational.models import StudentLevels
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.national_programs import NationalProgramModel
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.routes.shared.validation import phone_number_validator
from pcapi.serialization.utils import to_camel
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils


class ListCollectiveOffersQueryModel(BaseModel):
    offerStatus: CollectiveOfferDisplayedStatus | None = fields.COLLECTIVE_OFFER_OFFER_STATUS
    venue_id: int | None = fields.VENUE_ID
    period_beginning_date: datetime | None = fields.PERIOD_BEGINNING_DATE
    period_ending_date: datetime | None = fields.PERIOD_ENDING_DATE

    class Config:
        alias_generator = to_camel
        extra = "forbid"


def validate_email(email: str) -> str:
    if not email:
        raise ValueError("Ce champ ne peut pas être vide")
    if not email_utils.is_valid_email(email):
        raise ValueError(f"{email} n'est pas une adresse mail valide")
    return email


def validate_emails(emails: list[str]) -> list[str]:
    if not emails:
        raise ValueError("Un email doit être renseigné.")
    for email in emails:
        if not email_utils.is_valid_email(email):
            raise ValueError(f"{email} n'est pas une adresse mail valide")
    return emails


def validate_number_of_tickets(number_of_tickets: int | None) -> int:
    if number_of_tickets is None:
        raise ValueError("Le nombre de places ne peut pas être nul.")
    if number_of_tickets < 0:
        raise ValueError("Le nombre de places ne peut pas être négatif.")
    return number_of_tickets


def validate_price(price: float | None) -> float:
    if price is None:
        raise ValueError("Le prix ne peut pas être nul.")
    if price < 0:
        raise ValueError("Le prix ne peut pas être négatif.")
    return price


def validate_booking_limit_datetime(
    booking_limit_datetime: datetime | None, values: dict[str, typing.Any]
) -> datetime | None:
    if (
        booking_limit_datetime is not None
        and "start_datetime" in values
        and booking_limit_datetime > values["start_datetime"]
    ):
        raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
    return booking_limit_datetime


def validate_start_datetime(start_datetime: datetime | None, values: dict[str, typing.Any]) -> datetime | None:
    # we need a datetime with timezone information which is not provided by date_utils.get_naive_utc_now.
    if not start_datetime:
        return None

    if start_datetime.tzinfo is not None:
        if start_datetime < datetime.now(timezone.utc):
            raise ValueError("L'évènement ne peut commencer dans le passé.")
    elif start_datetime < date_utils.get_naive_utc_now():
        raise ValueError("L'évènement ne peut commencer dans le passé.")
    return start_datetime


def validate_end_datetime(end_datetime: datetime | None, values: dict[str, typing.Any]) -> datetime | None:
    # we need a datetime with timezone information which is not provided by date_utils.get_naive_utc_now.
    if not end_datetime:
        return None

    if end_datetime.tzinfo is not None:
        if end_datetime < datetime.now(timezone.utc):
            raise ValueError("L'évènement ne peut se terminer dans le passé.")
    elif end_datetime < date_utils.get_naive_utc_now():
        raise ValueError("L'évènement ne peut se terminer dans le passé.")
    return end_datetime


def validate_price_detail(price_detail: str | None) -> str | None:
    if price_detail and len(price_detail) > 1000:
        raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
    return price_detail


def validate_image_file(image_file: str | None) -> str | None:
    if image_file is None:
        return None
    if not image_file or len(image_file) % 4 != 0:
        # empty string case
        raise ValueError("Ce champ doit contenir une image en base 64 valide")
    if len(image_file) > 2000000:
        raise ValueError("L'image ne doit pas faire plus de 1.5 Mio (2 000 000 caractères en base 64)")
    return image_file


def number_of_tickets_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_number_of_tickets)


def price_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_price)


def booking_limit_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_booking_limit_datetime)


def start_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_start_datetime)


def end_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_end_datetime)


def price_detail_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_price_detail)


def email_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_email)


def emails_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_emails)


def image_file_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_image_file)


class CollectiveBookingResponseModel(BaseModel):
    id: int = fields.COLLECTIVE_BOOKING_ID
    status: CollectiveBookingStatus = fields.COLLECTIVE_BOOKING_STATUS
    confirmationDate: datetime | None = fields.COLLECTIVE_BOOKING_CONFIRMATION_DATE
    cancellationLimitDate: datetime | None = fields.COLLECTIVE_BOOKING_CANCELLATION_LIMIT_DATE
    reimbursementDate: datetime | None = fields.COLLECTIVE_BOOKING_REIMBURSED_DATA
    dateUsed: datetime | None = fields.COLLECTIVE_BOOKING_DATE_USED
    dateCreated: datetime = fields.COLLECTIVE_BOOKING_DATE_CREATED

    class Config:
        orm_mode = True


class CollectiveOffersResponseModel(BaseModel):
    id: int = fields.COLLECTIVE_OFFER_ID
    startDatetime: str = fields.COLLECTIVE_OFFER_START_DATETIME
    endDatetime: str = fields.COLLECTIVE_OFFER_END_DATETIME
    offerStatus: str = fields.COLLECTIVE_OFFER_OFFER_STATUS
    venueId: int = fields.VENUE_ID
    bookings: typing.Sequence[CollectiveBookingResponseModel]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "CollectiveOffersResponseModel":
        return cls(
            id=offer.id,
            startDatetime=offer.collectiveStock.startDatetime.replace(microsecond=0).isoformat(),
            endDatetime=offer.collectiveStock.endDatetime.replace(microsecond=0).isoformat(),
            offerStatus=offer.displayedStatus.value,
            venueId=offer.venueId,
            bookings=offer.collectiveStock.collectiveBookings,
        )


class CollectiveOffersListResponseModel(BaseModel):
    __root__: list[CollectiveOffersResponseModel]


class CollectiveOfferLocationSchoolModel(BaseModel):
    type: typing.Literal["SCHOOL"] = fields.COLLECTIVE_OFFER_LOCATION_TYPE

    class Config:
        title = CollectiveLocationType.SCHOOL.value
        extra = "forbid"


class CollectiveOfferLocationToBeDefinedModel(BaseModel):
    type: typing.Literal["TO_BE_DEFINED"] = fields.COLLECTIVE_OFFER_LOCATION_TYPE
    comment: str | None = fields.COLLECTIVE_OFFER_LOCATION_COMMENT

    class Config:
        title = CollectiveLocationType.TO_BE_DEFINED.value
        extra = "forbid"


class CollectiveOfferLocationAddressVenueModel(BaseModel):
    type: typing.Literal["ADDRESS"] = fields.COLLECTIVE_OFFER_LOCATION_TYPE
    isVenueAddress: typing.Literal[True] = fields.COLLECTIVE_OFFER_LOCATION_IS_VENUE_ADDRESS

    class Config:
        title = "ADDRESS - VENUE"
        extra = "forbid"


class CollectiveOfferLocationAddressModel(BaseModel):
    type: typing.Literal["ADDRESS"] = fields.COLLECTIVE_OFFER_LOCATION_TYPE
    addressLabel: str | None = fields.COLLECTIVE_OFFER_LOCATION_ADDRESS_LABEL
    addressId: int = fields.COLLECTIVE_OFFER_LOCATION_ADDRESS_ID
    isVenueAddress: typing.Literal[False] = fields.COLLECTIVE_OFFER_LOCATION_IS_VENUE_ADDRESS

    class Config:
        title = "ADDRESS - OTHER"
        extra = "forbid"


CollectiveOfferLocation = (
    CollectiveOfferLocationSchoolModel
    | CollectiveOfferLocationAddressVenueModel
    | CollectiveOfferLocationAddressModel
    | CollectiveOfferLocationToBeDefinedModel
)


def _validate_location(location: typing.Any) -> None:
    """
    Default pydantic error messages for a complex union like CollectiveOfferLocation are not very readable
    as pydantic will try and apply each type of the union to the field and output all the errors
    We manually generate a clear error message for each possible location field error
    """

    if not isinstance(location, dict):
        raise ValueError("Le champ location doit être un objet")

    location_type = location.get("type")
    if location_type is None:
        raise ValueError("Le champ type est requis")

    location_fields = set(location.keys())
    match location_type:
        case CollectiveLocationType.SCHOOL.value:
            allowed_fields = {"type"}
            if location_fields - allowed_fields:
                raise ValueError("Quand type=SCHOOL, aucun autre champ n'est accepté")

        case CollectiveLocationType.ADDRESS.value:
            allowed_fields = {"type", "isVenueAddress", "addressId", "addressLabel"}
            if location_fields - allowed_fields:
                raise ValueError(
                    "Quand type=ADDRESS, seuls les champs isVenueAddress, addressId, addressLabel sont acceptés"
                )

            is_venue_address = location.get("isVenueAddress")
            if not isinstance(is_venue_address, bool):
                raise ValueError("Quand type=ADDRESS, isVenueAddress est requis")

            if is_venue_address:
                allowed_fields = {"type", "isVenueAddress"}
                if location_fields - allowed_fields:
                    raise ValueError("Quand type=ADDRESS et isVenueAddress=true, aucun autre champ n'est accepté")
            elif "addressId" not in location:
                raise ValueError("Quand type=ADDRESS et isVenueAddress=false, le champ addressId est requis")

        case CollectiveLocationType.TO_BE_DEFINED.value:
            allowed_fields = {"type", "comment"}
            if location_fields - allowed_fields:
                raise ValueError("Quand type=TO_BE_DEFINED, seul le champ comment est accepté")

        case _:
            allowed_types = [t.name for t in CollectiveLocationType]
            raise ValueError(f"Les valeurs autorisées pour le champ type sont {', '.join(allowed_types)}")


def get_collective_offer_location_from_offer(offer: CollectiveOffer) -> CollectiveOfferLocation:
    match offer.locationType:
        case CollectiveLocationType.SCHOOL:
            return CollectiveOfferLocationSchoolModel(type=CollectiveLocationType.SCHOOL.value)
        case CollectiveLocationType.TO_BE_DEFINED:
            return CollectiveOfferLocationToBeDefinedModel(
                type=CollectiveLocationType.TO_BE_DEFINED.value,
                comment=offer.locationComment,
            )
        case CollectiveLocationType.ADDRESS:
            is_venue_address = (
                offer.offererAddress is not None
                and offer.offererAddress.addressId == offer.venue.offererAddress.addressId
                and offer.offererAddress.label == offer.venue.common_name
            )
            if is_venue_address:
                return CollectiveOfferLocationAddressVenueModel(
                    type=CollectiveLocationType.ADDRESS.value, isVenueAddress=True
                )
            else:
                assert offer.offererAddress
                return CollectiveOfferLocationAddressModel(
                    type=CollectiveLocationType.ADDRESS.value,
                    isVenueAddress=False,
                    addressLabel=offer.offererAddress.label,
                    addressId=offer.offererAddress.addressId,
                )


class GetPublicCollectiveOfferResponseModel(BaseModel):
    id: int = fields.COLLECTIVE_OFFER_ID
    offerStatus: str = fields.COLLECTIVE_OFFER_OFFER_STATUS
    name: str = fields.COLLECTIVE_OFFER_NAME
    description: str | None = fields.COLLECTIVE_OFFER_DESCRIPTION
    bookingEmails: list[str] | None = fields.COLLECTIVE_OFFER_BOOKING_EMAILS
    contactEmail: str = fields.COLLECTIVE_OFFER_CONTACT_EMAIL
    contactPhone: str = fields.COLLECTIVE_OFFER_CONTACT_PHONE
    domains: list[int] = fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS
    durationMinutes: int | None = fields.DURATION_MINUTES
    interventionArea: list[str]
    students: list[str]
    dateCreated: str = fields.COLLECTIVE_OFFER_DATE_CREATED
    hasBookingLimitDatetimesPassed: bool
    venueId: int = fields.VENUE_ID
    audioDisabilityCompliant: bool | None = fields.AUDIO_DISABILITY_COMPLIANT
    mentalDisabilityCompliant: bool | None = fields.MENTAL_DISABILITY_COMPLIANT
    motorDisabilityCompliant: bool | None = fields.MOTOR_DISABILITY_COMPLIANT
    visualDisabilityCompliant: bool | None = fields.VISUAL_DISABILITY_COMPLIANT
    startDatetime: str = fields.COLLECTIVE_OFFER_START_DATETIME
    endDatetime: str = fields.COLLECTIVE_OFFER_END_DATETIME
    bookingLimitDatetime: str = fields.COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME
    price: decimal.Decimal = fields.COLLECTIVE_OFFER_TOTAL_PRICE
    numberOfTickets: int = fields.COLLECTIVE_OFFER_NB_OF_TICKETS
    priceDetail: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL
    educationalInstitution: str | None = fields.EDUCATIONAL_INSTITUTION_UAI
    educationalInstitutionId: int | None = fields.EDUCATIONAL_INSTITUTION_ID
    location: CollectiveOfferLocation = fields.COLLECTIVE_OFFER_LOCATION
    imageCredit: str | None = fields.IMAGE_CREDIT
    imageUrl: str | None = fields.IMAGE_URL
    bookings: typing.Sequence[CollectiveBookingResponseModel]
    nationalProgram: NationalProgramModel | None
    formats: list[EacFormat] = fields.COLLECTIVE_OFFER_FORMATS

    class Config:
        extra = "forbid"
        orm_mode = True
        allow_population_by_field_name = True

    @classmethod
    def from_orm(
        cls: type["GetPublicCollectiveOfferResponseModel"], offer: CollectiveOffer
    ) -> "GetPublicCollectiveOfferResponseModel":
        location = get_collective_offer_location_from_offer(offer)

        return cls(
            id=offer.id,
            offerStatus=offer.displayedStatus.value,
            name=offer.name,
            description=offer.description,
            bookingEmails=offer.bookingEmails,
            contactEmail=offer.contactEmail,  # type: ignore[arg-type]
            contactPhone=offer.contactPhone,  # type: ignore[arg-type]
            domains=[domain.id for domain in offer.domains],
            durationMinutes=offer.durationMinutes,
            interventionArea=offer.interventionArea,
            students=[student.name for student in offer.students],
            dateCreated=offer.dateCreated.replace(microsecond=0).isoformat(),
            hasBookingLimitDatetimesPassed=offer.hasBookingLimitDatetimesPassed,
            venueId=offer.venueId,
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
            startDatetime=offer.collectiveStock.startDatetime.replace(microsecond=0).isoformat(),
            endDatetime=offer.collectiveStock.endDatetime.replace(microsecond=0).isoformat(),
            bookingLimitDatetime=offer.collectiveStock.bookingLimitDatetime.replace(microsecond=0).isoformat(),
            price=offer.collectiveStock.price,
            numberOfTickets=offer.collectiveStock.numberOfTickets,
            priceDetail=offer.collectiveStock.priceDetail,
            educationalInstitution=offer.institution.institutionId if offer.institution else None,
            educationalInstitutionId=offer.institution.id if offer.institution else None,
            location=location,
            imageCredit=offer.imageCredit,
            imageUrl=offer.imageUrl,
            bookings=offer.collectiveStock.collectiveBookings,
            nationalProgram=offer.nationalProgram,
            formats=offer.formats,
        )


class GetCollectiveFormatModel(BaseModel):
    id: str
    name: str


class GetCollectiveFormatListModel(BaseModel):
    __root__: list[GetCollectiveFormatModel]


class PostCollectiveOfferBodyModel(BaseModel):
    # offer part
    venue_id: int = fields.VENUE_ID
    name: str = fields.COLLECTIVE_OFFER_NAME
    description: str = fields.COLLECTIVE_OFFER_DESCRIPTION
    formats: list[EacFormat] = fields.COLLECTIVE_OFFER_FORMATS
    booking_emails: list[str] = fields.COLLECTIVE_OFFER_BOOKING_EMAILS
    contact_email: str = fields.COLLECTIVE_OFFER_CONTACT_EMAIL
    contact_phone: str = fields.COLLECTIVE_OFFER_CONTACT_PHONE
    domains: list[int] = fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS
    duration_minutes: int | None = fields.DURATION_MINUTES
    students: list[str] = fields.COLLECTIVE_OFFER_STUDENT_LEVELS
    audio_disability_compliant: bool = fields.AUDIO_DISABILITY_COMPLIANT_WITH_DEFAULT
    mental_disability_compliant: bool = fields.MENTAL_DISABILITY_COMPLIANT_WITH_DEFAULT
    motor_disability_compliant: bool = fields.MOTOR_DISABILITY_COMPLIANT_WITH_DEFAULT
    visual_disability_compliant: bool = fields.VISUAL_DISABILITY_COMPLIANT_WITH_DEFAULT
    location: CollectiveOfferLocation = fields.COLLECTIVE_OFFER_LOCATION
    image_file: str | None = fields.IMAGE_FILE
    image_credit: str | None = fields.IMAGE_CREDIT
    national_program_id: int | None = fields.COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID
    # stock part
    start_datetime: datetime = fields.COLLECTIVE_OFFER_START_DATETIME
    end_datetime: datetime | None = fields.COLLECTIVE_OFFER_END_DATETIME
    booking_limit_datetime: datetime = fields.COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME
    total_price: decimal.Decimal = fields.COLLECTIVE_OFFER_TOTAL_PRICE
    number_of_tickets: int = fields.COLLECTIVE_OFFER_NB_OF_TICKETS
    price_detail: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL
    # link to educational institution
    educational_institution_id: int | None = fields.EDUCATIONAL_INSTITUTION_ID
    educational_institution: str | None = fields.EDUCATIONAL_INSTITUTION_UAI

    _validate_number_of_tickets = number_of_tickets_validator("number_of_tickets")
    _validate_total_price = price_validator("total_price")
    _validate_start_datetime = start_datetime_validator("start_datetime")
    _validate_end_datetime = end_datetime_validator("end_datetime")
    _validate_booking_limit_datetime = booking_limit_datetime_validator("booking_limit_datetime")
    _validate_price_detail = price_detail_validator("price_detail")
    _validate_contact_phone = phone_number_validator("contact_phone")
    _validate_booking_emails = emails_validator("booking_emails")
    _validate_contact_email = email_validator("contact_email")
    _validate_image_file = image_file_validator("image_file")

    @validator("students")
    def validate_students(cls, students: list[str]) -> list[StudentLevels]:
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
        if len(domains) == 0:
            raise ValueError("domains must have at least one value")
        return domains

    @validator("formats")
    def validate_formats(cls, formats: list[EacFormat]) -> list[EacFormat]:
        if len(formats) == 0:
            raise ValueError("formats must have at least one value")
        return formats

    @root_validator(pre=True)
    def image_validator(cls, values: dict) -> dict:
        image = values.get("image_file")
        credit = values.get("image_credit")
        if (image is not None and credit is None) or (credit is not None and image is None):
            raise ValueError(
                "Les champs imageFile et imageCredit sont liés, si l'un est rempli l'autre doit l'être aussi"
            )
        return values

    @root_validator(pre=True)
    def institution_validator(cls, values: dict) -> dict:
        institution_id = values.get("educationalInstitutionId")
        uai = values.get("educationalInstitution")
        if institution_id is not None and uai is not None:
            raise ValueError(
                "Les champs educationalInstitution et educationalInstitutionId sont mutuellement exclusifs. "
                "Vous ne pouvez pas remplir les deux en même temps"
            )
        if institution_id is None and uai is None:
            raise ValueError(
                "Le remplissage de l'un des champs educationalInstitution ou educationalInstitutionId est obligatoire."
            )

        return values

    @validator("end_datetime", pre=False)
    def validate_end_datetime_vs_start_datetime(
        cls, end_datetime: datetime | None, values: dict[str, typing.Any]
    ) -> datetime | None:
        start_datetime = values.get("start_datetime")
        if not start_datetime or not end_datetime:
            return None

        if end_datetime < start_datetime:
            raise ValueError("La date de fin de l'évènement ne peut précéder la date de début.")
        return end_datetime

    @validator("location", pre=True)
    def location_validator(cls, location: typing.Any) -> dict:
        _validate_location(location)
        return location

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchCollectiveOfferBodyModel(BaseModel):
    name: str | None = fields.COLLECTIVE_OFFER_NAME
    description: str | None = fields.COLLECTIVE_OFFER_DESCRIPTION
    venueId: int | None = fields.VENUE_ID
    formats: list[EacFormat] | None = fields.COLLECTIVE_OFFER_FORMATS
    bookingEmails: list[str] | None = fields.COLLECTIVE_OFFER_BOOKING_EMAILS
    contactEmail: str | None = fields.COLLECTIVE_OFFER_CONTACT_EMAIL
    contactPhone: str | None = fields.COLLECTIVE_OFFER_CONTACT_PHONE
    domains: list[int] | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS
    students: list[str] | None = fields.COLLECTIVE_OFFER_STUDENT_LEVELS
    location: CollectiveOfferLocation | None = fields.COLLECTIVE_OFFER_LOCATION
    interventionArea: list[str] | None = fields.COLLECTIVE_OFFER_INTERVENTION_AREA
    durationMinutes: int | None = fields.DURATION_MINUTES
    audioDisabilityCompliant: bool | None = fields.AUDIO_DISABILITY_COMPLIANT
    mentalDisabilityCompliant: bool | None = fields.MENTAL_DISABILITY_COMPLIANT
    motorDisabilityCompliant: bool | None = fields.MOTOR_DISABILITY_COMPLIANT
    visualDisabilityCompliant: bool | None = fields.VISUAL_DISABILITY_COMPLIANT

    imageCredit: str | None = fields.IMAGE_CREDIT
    imageFile: str | None = fields.IMAGE_FILE
    nationalProgramId: int | None = fields.COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID
    # stock part
    startDatetime: datetime | None = fields.COLLECTIVE_OFFER_START_DATETIME
    endDatetime: datetime | None = fields.COLLECTIVE_OFFER_END_DATETIME
    bookingLimitDatetime: datetime | None = fields.COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME
    price: float | None = fields.COLLECTIVE_OFFER_TOTAL_PRICE
    priceDetail: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL
    numberOfTickets: int | None = fields.COLLECTIVE_OFFER_NB_OF_TICKETS
    # educational_institution
    educationalInstitutionId: int | None = fields.EDUCATIONAL_INSTITUTION_ID
    educationalInstitution: str | None = fields.EDUCATIONAL_INSTITUTION_UAI

    _validate_number_of_tickets = number_of_tickets_validator("numberOfTickets")
    _validate_total_price = price_validator("price")
    _validate_price_detail = price_detail_validator("priceDetail")
    _validate_start_datetime = start_datetime_validator("startDatetime")
    _validate_end_datetime = end_datetime_validator("endDatetime")
    _validate_contact_phone = phone_number_validator("contactPhone")
    _validate_booking_emails = emails_validator("bookingEmails")
    _validate_contact_email = email_validator("contactEmail")

    @validator("students")
    def validate_students(cls, students: list[str] | None) -> list[StudentLevels] | None:
        # TODO(jeremieb): normalize students fields: use enum, not str
        if not students:
            return None

        return shared_offers.validate_students(students)

    @validator("formats")
    def validate_formats(cls, formats: list[EacFormat] | None) -> list[EacFormat]:
        if formats is None or len(formats) == 0:
            raise ValueError("formats must have at least one value")
        return formats

    @validator("name", allow_reuse=True)
    def validate_name(cls, name: str | None) -> str | None:
        if name is None or name.strip() == "":
            raise ValueError("name cannot be empty")

        educational_validation.check_collective_offer_name_length_is_valid(name)
        return name

    @validator("description")
    def validate_description(cls, description: str | None) -> str | None:
        if description is not None:
            educational_validation.check_collective_offer_description_length_is_valid(description)

        return description

    @validator("domains")
    def validate_domains(cls, domains: list[int] | None) -> list[int]:
        if domains is None or len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    @validator("bookingLimitDatetime")
    def validate_booking_limit_datetime(
        cls, booking_limit_datetime: datetime | None, values: dict[str, typing.Any]
    ) -> datetime | None:
        start = values.get("startDatetime")
        if booking_limit_datetime is not None and start is not None and booking_limit_datetime > start:
            raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
        return booking_limit_datetime

    @validator("startDatetime", pre=True)
    def validate_start_limit_datetime(cls, startDatetime: datetime | None) -> datetime | None:
        if startDatetime is None:
            raise ValueError("La date de début de l'évènement ne peut pas être vide.")
        return startDatetime

    @validator("endDatetime", pre=False)
    def validate_end_limit_datetime(
        cls, endDatetime: datetime | None, values: dict[str, typing.Any]
    ) -> datetime | None:
        start_datetime = values.get("startDatetime")
        if not endDatetime:
            raise ValueError("La date de fin de l'évènement ne peut pas être vide.")
        if start_datetime and endDatetime < start_datetime:
            raise ValueError("La date de fin de l'évènement ne peut précéder la date de début.")
        return endDatetime

    @root_validator(pre=True)
    def institution_validator(cls, values: dict) -> dict:
        institution_id = values.get("educationalInstitutionId")
        uai = values.get("educationalInstitution")
        if institution_id is not None and uai is not None:
            raise ValueError(
                "Les champs educationalInstitution et educationalInstitutionId sont mutuellement exclusifs. "
                "Vous ne pouvez pas remplir les deux en même temps"
            )

        return values

    @validator("location", pre=True)
    def location_validator(cls, location: typing.Any) -> dict:
        if location is not None:
            _validate_location(location)
        return location

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class ArchiveCollectiveOfferBodyModel(BaseModel):
    ids: list[int] = fields.COLLECTIVE_OFFER_IDS

    class Config:
        alias_generator = to_camel
        extra = "forbid"

    @validator("ids")
    def validate_ids(cls, ids: list[int]) -> list[int]:
        if len(ids) == 0:
            raise ValueError("ids must have at least one value")
        return ids
