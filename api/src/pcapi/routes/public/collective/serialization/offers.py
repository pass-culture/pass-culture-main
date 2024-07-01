from datetime import datetime
from datetime import timezone
import decimal
from typing import Any
from typing import Sequence

from pydantic.v1 import Field
from pydantic.v1 import root_validator
from pydantic.v1 import validator

import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import StudentLevels
from pcapi.models.offer_mixin import CollectiveOfferStatus
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization.collective_offers_serialize import validate_venue_id
from pcapi.routes.serialization.national_programs import NationalProgramModel
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.routes.shared.validation import phone_number_validator
from pcapi.serialization.utils import to_camel
from pcapi.utils import email as email_utils
from pcapi.validation.routes.offers import check_collective_offer_name_length_is_valid


class ListCollectiveOffersQueryModel(BaseModel):
    status: CollectiveOfferStatus | None = fields.COLLECTIVE_OFFER_STATUS
    venue_id: int | None = fields.VENUE_ID
    period_beginning_date: str | None = fields.PERIOD_BEGINNING_DATE
    period_ending_date: str | None = fields.PERIOD_ENDING_DATE

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferVenueModel(BaseModel):
    venueId: int | None = fields.VENUE_ID
    otherAddress: str | None
    addressType: collective_offers_serialize.OfferAddressType

    _validated_venue_id = validator("venueId", pre=True, allow_reuse=True)(validate_venue_id)

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


def validate_booking_limit_datetime(booking_limit_datetime: datetime | None, values: dict[str, Any]) -> datetime | None:
    if (
        booking_limit_datetime
        and "beginning_datetime" in values
        and booking_limit_datetime > values["beginning_datetime"]
    ):
        raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
    return booking_limit_datetime


def validate_beginning_datetime(beginning_datetime: datetime, values: dict[str, Any]) -> datetime:
    # we need a datetime with timezone information which is not provided by datetime.utcnow.
    if beginning_datetime.tzinfo is not None:
        if beginning_datetime < datetime.now(timezone.utc):  # pylint: disable=datetime-now
            raise ValueError("L'évènement ne peut commencer dans le passé.")
    elif beginning_datetime < datetime.utcnow():
        raise ValueError("L'évènement ne peut commencer dans le passé.")
    return beginning_datetime


def validate_start_datetime(start_datetime: datetime, values: dict[str, Any]) -> datetime:
    # we need a datetime with timezone information which is not provided by datetime.utcnow.
    if start_datetime.tzinfo is not None:
        if start_datetime < datetime.now(timezone.utc):  # pylint: disable=datetime-now
            raise ValueError("L'évènement ne peut commencer dans le passé.")
    elif start_datetime < datetime.utcnow():
        raise ValueError("L'évènement ne peut commencer dans le passé.")
    return start_datetime


def validate_end_datetime(end_datetime: datetime, values: dict[str, Any]) -> datetime:
    # we need a datetime with timezone information which is not provided by datetime.utcnow.
    if end_datetime.tzinfo is not None:
        if end_datetime < datetime.now(timezone.utc):  # pylint: disable=datetime-now
            raise ValueError("L'évènement ne peut se terminer dans le passé.")
    elif end_datetime < datetime.utcnow():
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
    return validator(field_name, allow_reuse=True, pre=True)(validate_number_of_tickets)


def price_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_price)


def booking_limit_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_booking_limit_datetime)


def beginning_datetime_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_beginning_datetime)


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
    beginningDatetime: str = fields.COLLECTIVE_OFFER_BEGINNING_DATETIME
    startDatetime: str = fields.COLLECTIVE_OFFER_START_DATETIME
    endDatetime: str = fields.COLLECTIVE_OFFER_END_DATETIME
    status: str = fields.COLLECTIVE_OFFER_STATUS
    venueId: int = fields.VENUE_ID
    bookings: Sequence[CollectiveBookingResponseModel]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "CollectiveOffersResponseModel":
        bookings = [
            CollectiveBookingResponseModel.from_orm(booking) for booking in offer.collectiveStock.collectiveBookings
        ]
        return cls(
            id=offer.id,
            beginningDatetime=offer.collectiveStock.beginningDatetime.replace(microsecond=0).isoformat(),
            startDatetime=offer.collectiveStock.startDatetime.replace(microsecond=0).isoformat(),
            endDatetime=offer.collectiveStock.endDatetime.replace(microsecond=0).isoformat(),
            status=offer.status.value,
            venueId=offer.venueId,
            bookings=bookings,
        )


class CollectiveOffersListResponseModel(BaseModel):
    __root__: list[CollectiveOffersResponseModel]


class CollectiveOffersSubCategoryResponseModel(BaseModel):
    id: str
    label: str
    category: str
    categoryId: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, subcategory: subcategories.Subcategory) -> "CollectiveOffersSubCategoryResponseModel":
        return cls(
            id=subcategory.id,
            label=subcategory.pro_label,
            category=subcategory.category.pro_label,
            categoryId=subcategory.category.id,
        )


class CollectiveOffersListSubCategoriesResponseModel(BaseModel):
    __root__: list[CollectiveOffersSubCategoryResponseModel]


class CollectiveOffersCategoryResponseModel(BaseModel):
    id: str
    name: str


class CollectiveOffersListCategoriesResponseModel(BaseModel):
    __root__: list[CollectiveOffersCategoryResponseModel]


class GetPublicCollectiveOfferResponseModel(BaseModel):
    id: int = fields.COLLECTIVE_OFFER_ID
    status: str = fields.COLLECTIVE_OFFER_STATUS
    name: str = fields.COLLECTIVE_OFFER_NAME
    description: str | None = fields.COLLECTIVE_OFFER_DESCRIPTION
    subcategoryId: str | None = fields.COLLECTIVE_OFFER_SUBCATEGORY_ID
    bookingEmails: list[str] | None = fields.COLLECTIVE_OFFER_BOOKING_EMAILS
    contactEmail: str = fields.COLLECTIVE_OFFER_CONTACT_EMAIL
    contactPhone: str = fields.COLLECTIVE_OFFER_CONTACT_PHONE
    domains: list[int] = fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS
    durationMinutes: int | None = fields.DURATION_MINUTES
    interventionArea: list[str]
    students: list[str]
    dateCreated: str = fields.COLLECTIVE_OFFER_DATE_CREATED
    hasBookingLimitDatetimesPassed: bool
    isActive: bool | None = fields.COLLECTIVE_OFFER_IS_ACTIVE
    isSoldOut: bool = fields.COLLECTIVE_OFFER_IS_SOLD_OUT
    venueId: int = fields.VENUE_ID
    audioDisabilityCompliant: bool | None = fields.AUDIO_DISABILITY
    mentalDisabilityCompliant: bool | None = fields.MENTAL_DISABILITY
    motorDisabilityCompliant: bool | None = fields.MOTOR_DISABILITY
    visualDisabilityCompliant: bool | None = fields.VISUAL_DISABILITY
    beginningDatetime: str = fields.COLLECTIVE_OFFER_BEGINNING_DATETIME
    startDatetime: str = fields.COLLECTIVE_OFFER_START_DATETIME
    endDatetime: str = fields.COLLECTIVE_OFFER_END_DATETIME
    bookingLimitDatetime: str = fields.COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME
    totalPrice: decimal.Decimal = fields.COLLECTIVE_OFFER_TOTAL_PRICE
    numberOfTickets: int = fields.COLLECTIVE_OFFER_NB_OF_TICKETS
    educationalPriceDetail: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL
    educationalInstitution: str | None = fields.EDUCATIONAL_INSTITUTION_UAI
    educationalInstitutionId: int | None = fields.EDUCATIONAL_INSTITUTION_ID
    offerVenue: OfferVenueModel
    imageCredit: str | None = fields.IMAGE_CREDIT
    imageUrl: str | None = fields.IMAGE_URL
    bookings: Sequence[CollectiveBookingResponseModel]
    nationalProgram: NationalProgramModel | None
    formats: list[subcategories.EacFormat] | None = fields.COLLECTIVE_OFFER_FORMATS

    class Config:
        extra = "forbid"
        orm_mode = True

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "GetPublicCollectiveOfferResponseModel":
        if offer.nationalProgram:
            national_program = NationalProgramModel.from_orm(offer.nationalProgram)
        else:
            national_program = None

        bookings = [
            CollectiveBookingResponseModel.from_orm(booking) for booking in offer.collectiveStock.collectiveBookings
        ]
        return cls(
            id=offer.id,
            status=offer.status.name,
            name=offer.name,
            description=offer.description,
            subcategoryId=offer.subcategoryId,
            bookingEmails=offer.bookingEmails,
            contactEmail=offer.contactEmail,  # type: ignore[arg-type]
            contactPhone=offer.contactPhone,  # type: ignore[arg-type]
            domains=[domain.id for domain in offer.domains],
            durationMinutes=offer.durationMinutes,
            interventionArea=offer.interventionArea,
            students=[student.name for student in offer.students],
            dateCreated=offer.dateCreated.replace(microsecond=0).isoformat(),
            hasBookingLimitDatetimesPassed=offer.hasBookingLimitDatetimesPassed,
            isActive=offer.isActive,
            isSoldOut=offer.isSoldOut,
            venueId=offer.venueId,
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
            beginningDatetime=offer.collectiveStock.beginningDatetime.replace(microsecond=0).isoformat(),
            startDatetime=offer.collectiveStock.startDatetime.replace(microsecond=0).isoformat(),
            endDatetime=offer.collectiveStock.endDatetime.replace(microsecond=0).isoformat(),
            bookingLimitDatetime=offer.collectiveStock.bookingLimitDatetime.replace(microsecond=0).isoformat(),
            totalPrice=offer.collectiveStock.price,
            numberOfTickets=offer.collectiveStock.numberOfTickets,
            educationalPriceDetail=offer.collectiveStock.priceDetail,
            educationalInstitution=offer.institution.institutionId if offer.institutionId else None,
            educationalInstitutionId=offer.institution.id if offer.institutionId else None,
            offerVenue={  # type: ignore[arg-type]
                "venueId": offer.offerVenue.get("venueId"),
                "addressType": offer.offerVenue["addressType"],
                "otherAddress": offer.offerVenue["otherAddress"] or None,
            },
            imageCredit=offer.imageCredit,
            imageUrl=offer.imageUrl,
            bookings=bookings,
            nationalProgram=national_program,
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
    subcategory_id: str | None = fields.COLLECTIVE_OFFER_SUBCATEGORY_ID
    formats: list[subcategories.EacFormat] | None = fields.COLLECTIVE_OFFER_FORMATS
    booking_emails: list[str] = fields.COLLECTIVE_OFFER_BOOKING_EMAILS
    contact_email: str = fields.COLLECTIVE_OFFER_CONTACT_EMAIL
    contact_phone: str = fields.COLLECTIVE_OFFER_CONTACT_PHONE
    domains: list[int] = fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS
    duration_minutes: int | None = fields.DURATION_MINUTES
    students: list[str] = fields.COLLECTIVE_OFFER_STUDENT_LEVELS
    audio_disability_compliant: bool = fields.AUDIO_DISABILITY_WITH_DEFAULT
    mental_disability_compliant: bool = fields.MENTAL_DISABILITY_WITH_DEFAULT
    motor_disability_compliant: bool = fields.MOTOR_DISABILITY_WITH_DEFAULT
    visual_disability_compliant: bool = fields.VISUAL_DISABILITY_WITH_DEFAULT
    offer_venue: OfferVenueModel
    isActive: bool = fields.COLLECTIVE_OFFER_IS_ACTIVE
    image_file: str | None = fields.IMAGE_FILE
    image_credit: str | None = fields.IMAGE_CREDIT
    nationalProgramId: int | None = fields.COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID
    # stock part
    beginning_datetime: datetime = fields.COLLECTIVE_OFFER_BEGINNING_DATETIME
    start_datetime: datetime | None = fields.COLLECTIVE_OFFER_START_DATETIME
    end_datetime: datetime | None = fields.COLLECTIVE_OFFER_END_DATETIME
    booking_limit_datetime: datetime = fields.COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME
    total_price: decimal.Decimal = fields.COLLECTIVE_OFFER_TOTAL_PRICE
    number_of_tickets: int = fields.COLLECTIVE_OFFER_NB_OF_TICKETS
    educational_price_detail: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL
    # link to educational institution
    educational_institution_id: int | None = fields.EDUCATIONAL_INSTITUTION_ID
    educational_institution: str | None = fields.EDUCATIONAL_INSTITUTION_UAI

    _validate_number_of_tickets = number_of_tickets_validator("number_of_tickets")
    _validate_total_price = price_validator("total_price")
    _validate_beginning_datetime = beginning_datetime_validator("beginning_datetime")
    _validate_start_datetime = start_datetime_validator("start_datetime")
    _validate_end_datetime = end_datetime_validator("end_datetime")
    _validate_booking_limit_datetime = booking_limit_datetime_validator("booking_limit_datetime")
    _validate_educational_price_detail = price_detail_validator("educational_price_detail")
    _validate_contact_phone = phone_number_validator("contact_phone")
    _validate_booking_emails = emails_validator("booking_emails")
    _validate_contact_email = email_validator("contact_email")
    _validate_image_file = image_file_validator("image_file")

    @validator("students")
    def validate_students(cls, students: list[str]) -> list[StudentLevels]:
        return shared_offers.validate_students(students)

    @root_validator
    def validate_formats_and_subcategory(cls, values: dict) -> dict:
        formats = values.get("formats")
        if formats:
            return values

        subcategory_id = values.get("subcategory_id")
        if not subcategory_id:
            raise ValueError("subcategory_id & formats: at least one should not be null")

        try:
            subcategory = subcategories.COLLECTIVE_SUBCATEGORIES[subcategory_id]
        except KeyError:
            raise ValueError("Unknown subcategory id")

        values["formats"] = subcategory.formats
        return values

    @validator("name", pre=True)
    def validate_name(cls, name: str) -> str:
        check_collective_offer_name_length_is_valid(name)
        return name

    @validator("domains", pre=True)
    def validate_domains(cls, domains: list[str]) -> list[str]:
        if len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

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

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchCollectiveOfferBodyModel(BaseModel):
    name: str | None = fields.COLLECTIVE_OFFER_NAME
    description: str | None = fields.COLLECTIVE_OFFER_DESCRIPTION
    venueId: int | None = fields.VENUE_ID
    subcategoryId: str | None = fields.COLLECTIVE_OFFER_SUBCATEGORY_ID
    formats: list[subcategories.EacFormat] | None = fields.COLLECTIVE_OFFER_FORMATS
    bookingEmails: list[str] | None = fields.COLLECTIVE_OFFER_BOOKING_EMAILS
    contactEmail: str | None = fields.COLLECTIVE_OFFER_CONTACT_EMAIL
    contactPhone: str | None = fields.COLLECTIVE_OFFER_CONTACT_PHONE
    domains: list[int] | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS
    students: list[str] | None = fields.COLLECTIVE_OFFER_STUDENT_LEVELS
    offerVenue: OfferVenueModel | None
    interventionArea: list[str] | None
    durationMinutes: int | None = fields.DURATION_MINUTES
    audioDisabilityCompliant: bool | None = fields.AUDIO_DISABILITY
    mentalDisabilityCompliant: bool | None = fields.MENTAL_DISABILITY
    motorDisabilityCompliant: bool | None = fields.MOTOR_DISABILITY
    visualDisabilityCompliant: bool | None = fields.VISUAL_DISABILITY

    isActive: bool | None = fields.COLLECTIVE_OFFER_IS_ACTIVE
    imageCredit: str | None = fields.IMAGE_CREDIT
    imageFile: str | None = fields.IMAGE_FILE
    nationalProgramId: int | None = fields.COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID
    # stock part
    beginningDatetime: datetime | None = fields.COLLECTIVE_OFFER_BEGINNING_DATETIME
    startDatetime: datetime | None = fields.COLLECTIVE_OFFER_START_DATETIME
    endDatetime: datetime | None = fields.COLLECTIVE_OFFER_END_DATETIME
    bookingLimitDatetime: datetime | None = fields.COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME
    price: float | None = Field(
        None,
        description="Collective offer price (in €)",  # TODO: Harmonize with Creation
        example=100.00,
        alias="totalPrice",
    )
    educationalPriceDetail: str | None = fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL
    numberOfTickets: int | None = fields.COLLECTIVE_OFFER_NB_OF_TICKETS
    # educational_institution
    educationalInstitutionId: int | None = fields.EDUCATIONAL_INSTITUTION_ID
    educationalInstitution: str | None = fields.EDUCATIONAL_INSTITUTION_UAI

    _validate_number_of_tickets = number_of_tickets_validator("numberOfTickets")
    _validate_total_price = price_validator("price")
    _validate_educational_price_detail = price_detail_validator("educationalPriceDetail")
    _validate_beginning_datetime = beginning_datetime_validator("beginningDatetime")
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

    @validator("domains")
    def validate_domains(cls, domains: list[int]) -> list[int]:
        if len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    @validator("name", allow_reuse=True)
    def validate_name(cls, name: str | None) -> str | None:
        assert name is not None and name.strip() != ""
        check_collective_offer_name_length_is_valid(name)
        return name

    @validator("domains")
    def validate_domains_collective_offer_edition(cls, domains: list[int] | None) -> list[int] | None:
        if domains is None or (domains is not None and len(domains) == 0):
            raise ValueError("domains must have at least one value")

        return domains

    @validator("bookingLimitDatetime")
    def validate_booking_limit_datetime(
        cls, booking_limit_datetime: datetime | None, values: dict[str, Any]
    ) -> datetime | None:
        if (
            booking_limit_datetime
            and values.get("beginningDatetime", None) is not None
            and booking_limit_datetime > values["beginningDatetime"]
        ):
            raise ValueError("La date limite de réservation ne peut être postérieure à la date de début de l'évènement")
        return booking_limit_datetime

    @validator("beginningDatetime", pre=True)
    def validate_beginning_limit_datetime(cls, beginningDatetime: datetime | None) -> datetime | None:
        if beginningDatetime is None:
            raise ValueError("La date de début de l'évènement ne peut pas être nulle.")
        return beginningDatetime

    @validator("startDatetime", pre=True)
    def validate_start_limit_datetime(cls, startDatetime: datetime | None) -> datetime | None:
        if startDatetime is None:
            raise ValueError("La date de début de l'évènement ne peut pas être vide.")
        return startDatetime

    @validator("endDatetime", pre=True)
    def validate_end_limit_datetime(cls, endDatetime: datetime | None, values: dict[str, Any]) -> datetime | None:
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

    class Config:
        alias_generator = to_camel
        extra = "forbid"
