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
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.public.documentation_constants import fields
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
    status: OfferStatus | None = Field(
        None,
        description=fields.OFFER_STATUS_FIELD_DATA.description,
        example=fields.OFFER_STATUS_FIELD_DATA.example,
    )
    venue_id: int | None = Field(
        None,
        description=fields.VENUE_ID_FIELD_DATA.description,
        example=fields.VENUE_ID_FIELD_DATA.example,
    )
    period_beginning_date: str | None = Field(
        None,
        description=fields.PERIOD_BEGINNING_DATE_FIELD_DATA.description,
        example=fields.PERIOD_BEGINNING_DATE_FIELD_DATA.example,
    )
    period_ending_date: str | None = Field(
        None,
        description=fields.PERIOD_ENDING_DATE_FIELD_DATA.description,
        example=fields.PERIOD_ENDING_DATE_FIELD_DATA.example,
    )

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferVenueModel(BaseModel):
    venueId: int | None = Field(
        None, description=fields.VENUE_ID_FIELD_DATA.description, example=fields.VENUE_ID_FIELD_DATA.example
    )
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


def price_detail_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_price_detail)


def email_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_email)


def emails_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_emails)


def image_file_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True, pre=True)(validate_image_file)


class CollectiveBookingResponseModel(BaseModel):
    id: int
    status: CollectiveBookingStatus
    confirmationDate: datetime | None
    cancellationLimitDate: datetime | None
    reimbursementDate: datetime | None
    dateUsed: datetime | None
    dateCreated: datetime

    class Config:
        orm_mode = True


class CollectiveOffersResponseModel(BaseModel):
    id: int
    beginningDatetime: str
    status: str
    venueId: int
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
    id: int
    status: str
    name: str
    description: str | None
    subcategoryId: str | None
    bookingEmails: list[str] | None
    contactEmail: str
    contactPhone: str
    domains: list[int]
    durationMinutes: int | None
    interventionArea: list[str]
    students: list[str]
    dateCreated: str
    hasBookingLimitDatetimesPassed: bool
    isActive: bool | None
    isSoldOut: bool
    venueId: int
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None
    beginningDatetime: str
    bookingLimitDatetime: str
    totalPrice: decimal.Decimal
    numberOfTickets: int
    educationalPriceDetail: str | None
    educationalInstitution: str | None
    educationalInstitutionId: int | None
    offerVenue: OfferVenueModel
    imageCredit: str | None
    imageUrl: str | None
    bookings: Sequence[CollectiveBookingResponseModel]
    nationalProgram: NationalProgramModel | None
    formats: list[subcategories.EacFormat] | None

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
    venue_id: int = Field(..., description=fields.VENUE_ID_FIELD_DATA.description)
    name: str = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_NAME.description,
        example=fields.COLLECTIVE_OFFER_NAME.example,
    )
    description: str = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_DESCRIPTION.description,
        example=fields.COLLECTIVE_OFFER_DESCRIPTION.example,
    )
    subcategory_id: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_SUBCATEGORY_ID_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_SUBCATEGORY_ID_FIELD_DATA.example,
    )
    formats: list[subcategories.EacFormat] | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_FORMATS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_FORMATS_FIELD_DATA.example,
    )
    booking_emails: list[str] = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_BOOKING_EMAILS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_BOOKING_EMAILS_FIELD_DATA.example,
    )
    contact_email: str = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_CONTACT_EMAIL_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_CONTACT_EMAIL_FIELD_DATA.example,
    )
    contact_phone: str = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_CONTACT_PHONE_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_CONTACT_PHONE_FIELD_DATA.example,
    )
    domains: list[int] = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS_FIELD_DATA.example,
    )
    duration_minutes: int | None = Field(
        None,
        description=fields.DURATION_MINUTES_FIELD_DATA.description,
        example=fields.DURATION_MINUTES_FIELD_DATA.example,
    )
    students: list[str] = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_STUDENT_LEVELS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_STUDENT_LEVELS_FIELD_DATA.example,
    )
    audio_disability_compliant: bool = Field(
        False,
        description=fields.AUDIO_DISABILITY_FIELD_DATA.description,
        example=fields.AUDIO_DISABILITY_FIELD_DATA.example,
    )
    mental_disability_compliant: bool = Field(
        False,
        description=fields.MENTAL_DISABILITY_FIELD_DATA.description,
        example=fields.MENTAL_DISABILITY_FIELD_DATA.example,
    )
    motor_disability_compliant: bool = Field(
        False,
        description=fields.MOTOR_DISABILITY_FIELD_DATA.description,
        example=fields.MOTOR_DISABILITY_FIELD_DATA.example,
    )
    visual_disability_compliant: bool = Field(
        False,
        description=fields.VISUAL_DISABILITY_FIELD_DATA.description,
        example=fields.VISUAL_DISABILITY_FIELD_DATA.example,
    )
    offer_venue: OfferVenueModel
    isActive: bool = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_IS_ACTIVE_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_IS_ACTIVE_FIELD_DATA.example,
    )
    image_file: str | None = Field(
        None,
        description=fields.IMAGE_FILE_FIELD_DATA.description,
        example=fields.IMAGE_FILE_FIELD_DATA.example,
    )
    image_credit: str | None = Field(
        None,
        description=fields.IMAGE_CREDIT_FIELD_DATA.description,
        example=fields.IMAGE_CREDIT_FIELD_DATA.example,
    )
    nationalProgramId: int | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID_FIELD_DATA.example,
    )
    # stock part
    beginning_datetime: datetime = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_BEGINNING_DATETIME_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_BEGINNING_DATETIME_FIELD_DATA.example,
    )
    booking_limit_datetime: datetime = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_BOOKING_LIMIT_DATETIME_FIELD_DATA.example,
    )
    total_price: decimal.Decimal = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_TOTAL_PRICE_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_TOTAL_PRICE_FIELD_DATA.example,
    )
    number_of_tickets: int = Field(
        ...,
        description=fields.COLLECTIVE_OFFER_NB_OF_TICKETS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_NB_OF_TICKETS_FIELD_DATA.example,
    )
    educational_price_detail: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL_FIELD_DATA.example,
    )
    # link to educational institution
    educational_institution_id: int | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_ID_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_ID_FIELD_DATA.example,
    )
    educational_institution: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_FIELD_DATA.example,
    )

    _validate_number_of_tickets = number_of_tickets_validator("number_of_tickets")
    _validate_total_price = price_validator("total_price")
    _validate_beginning_datetime = beginning_datetime_validator("beginning_datetime")
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
    name: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_NAME.description,
        example=fields.COLLECTIVE_OFFER_NAME.example,
    )
    description: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_DESCRIPTION.description,
        example=fields.COLLECTIVE_OFFER_DESCRIPTION.example,
    )
    venueId: int | None = Field(
        None,
        description=fields.VENUE_ID_FIELD_DATA.description,
        example=fields.VENUE_ID_FIELD_DATA.example,
    )
    subcategoryId: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_SUBCATEGORY_ID_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_SUBCATEGORY_ID_FIELD_DATA.example,
    )
    formats: list[subcategories.EacFormat] | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_FORMATS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_FORMATS_FIELD_DATA.example,
    )
    bookingEmails: list[str] | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_BOOKING_EMAILS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_BOOKING_EMAILS_FIELD_DATA.example,
    )
    contactEmail: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_CONTACT_EMAIL_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_CONTACT_EMAIL_FIELD_DATA.example,
    )
    contactPhone: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_CONTACT_PHONE_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_CONTACT_PHONE_FIELD_DATA.example,
    )
    domains: list[int] | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_EDUCATIONAL_DOMAINS_FIELD_DATA.example,
    )
    students: list[str] | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_STUDENT_LEVELS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_STUDENT_LEVELS_FIELD_DATA.example,
    )
    offerVenue: OfferVenueModel | None
    interventionArea: list[str] | None
    durationMinutes: int | None = Field(
        None,
        description=fields.DURATION_MINUTES_FIELD_DATA.description,
        example=fields.DURATION_MINUTES_FIELD_DATA.example,
    )
    audioDisabilityCompliant: bool | None = Field(
        None,
        description=fields.AUDIO_DISABILITY_FIELD_DATA.description,
        example=fields.AUDIO_DISABILITY_FIELD_DATA.example,
    )
    mentalDisabilityCompliant: bool | None = Field(
        None,
        description=fields.MENTAL_DISABILITY_FIELD_DATA.description,
        example=fields.MENTAL_DISABILITY_FIELD_DATA.example,
    )
    motorDisabilityCompliant: bool | None = Field(
        None,
        description=fields.MOTOR_DISABILITY_FIELD_DATA.description,
        example=fields.MOTOR_DISABILITY_FIELD_DATA.example,
    )
    visualDisabilityCompliant: bool | None = Field(
        None,
        description=fields.VISUAL_DISABILITY_FIELD_DATA.description,
        example=fields.VISUAL_DISABILITY_FIELD_DATA.example,
    )
    isActive: bool | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_IS_ACTIVE_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_IS_ACTIVE_FIELD_DATA.example,
    )
    imageCredit: str | None = Field(
        None,
        description=fields.IMAGE_CREDIT_FIELD_DATA.description,
        example=fields.IMAGE_CREDIT_FIELD_DATA.example,
    )
    imageFile: str | None = Field(
        None,
        description=fields.IMAGE_FILE_FIELD_DATA.description,
        example=fields.IMAGE_FILE_FIELD_DATA.example,
    )
    nationalProgramId: int | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_NATIONAL_PROGRAM_ID_FIELD_DATA.example,
    )
    # stock part
    beginningDatetime: datetime | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_BEGINNING_DATETIME_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_BEGINNING_DATETIME_FIELD_DATA.example,
    )
    bookingLimitDatetime: datetime | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_BOOKING_EMAILS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_BOOKING_EMAILS_FIELD_DATA.example,
    )
    price: float | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_TOTAL_PRICE_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_TOTAL_PRICE_FIELD_DATA.example,
        alias="totalPrice",
    )
    educationalPriceDetail: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_EDUCATIONAL_PRICE_DETAIL_FIELD_DATA.example,
    )
    numberOfTickets: int | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_NB_OF_TICKETS_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_NB_OF_TICKETS_FIELD_DATA.example,
    )
    # educational_institution
    educationalInstitutionId: int | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_ID_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_ID_FIELD_DATA.example,
    )
    educationalInstitution: str | None = Field(
        None,
        description=fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_FIELD_DATA.description,
        example=fields.COLLECTIVE_OFFER_EDUCATIONAL_INSTITUTION_FIELD_DATA.example,
    )

    _validate_number_of_tickets = number_of_tickets_validator("numberOfTickets")
    _validate_total_price = price_validator("price")
    _validate_educational_price_detail = price_detail_validator("educationalPriceDetail")
    _validate_beginning_datetime = beginning_datetime_validator("beginningDatetime")
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
