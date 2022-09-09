from datetime import datetime
from datetime import timezone
from typing import Any

from pydantic import Field
from pydantic import validator

from pcapi.core.categories import subcategories_v2
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import StudentLevels
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.serialization.utils import to_camel
from pcapi.utils.human_ids import dehumanize
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


class AuthErrorResponseModel(BaseModel):
    # only used as documentation for openapi
    errors: dict[str, str]


class ErrorResponseModel(BaseModel):
    # only used as documentation for openapi
    errors: dict[str, list[str]]


class ListCollectiveOffersQueryModel(BaseModel):
    status: OfferStatus | None
    venue_id: int | None
    period_beginning_date: str | None
    period_ending_date: str | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class OfferVenueModel(BaseModel):
    addressType: collective_offers_serialize.OfferAddressType
    venueId: int | None
    otherAddress: str | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"

    @validator("venueId")
    def validate_venueId(  # pylint: disable=no-self-argument
        cls: "OfferVenueModel", venueId: int | None, values: dict
    ) -> int | None:
        if values["addressType"] == collective_offers_serialize.OfferAddressType.OFFERER_VENUE and venueId is None:
            raise ValueError(
                f"Ce champ est obligatoire si 'addressType' vaut '{collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value}'"
            )
        if values["addressType"] != collective_offers_serialize.OfferAddressType.OFFERER_VENUE and venueId is not None:
            raise ValueError(
                f"Ce champ est interdit si 'addressType' ne vaut pas '{collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value}'"
            )

        return venueId

    @validator("otherAddress")
    def validate_otherAddress(  # pylint: disable=no-self-argument
        cls: "OfferVenueModel", otherAddress: str | None, values: dict
    ) -> str | None:
        if values["addressType"] == collective_offers_serialize.OfferAddressType.OTHER and not otherAddress:
            raise ValueError(
                f"Ce champ est obligatoire si 'addressType' vaut '{collective_offers_serialize.OfferAddressType.OTHER.value}'"
            )
        if values["addressType"] != collective_offers_serialize.OfferAddressType.OTHER and otherAddress:
            raise ValueError(
                f"Ce champ est interdit si 'addressType' ne vaut pas '{collective_offers_serialize.OfferAddressType.OTHER.value}'"
            )

        return otherAddress


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


class CollectiveOffersResponseModel(BaseModel):
    id: int
    beginningDatetime: str
    status: str
    venueId: int

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "CollectiveOffersResponseModel":
        return cls(
            id=offer.id,
            beginningDatetime=offer.collectiveStock.beginningDatetime.replace(microsecond=0).isoformat(),
            status=offer.status.value,  # type: ignore [attr-defined]
            venueId=offer.venueId,
        )


class CollectiveOffersListResponseModel(BaseModel):
    __root__: list[CollectiveOffersResponseModel]


class CollectiveOffersVenueResponseModel(BaseModel):
    id: int
    name: str
    address: str | None
    postalCode: str | None
    city: str | None

    class Config:
        orm_mode = True


class CollectiveOffersListVenuesResponseModel(BaseModel):
    __root__: list[CollectiveOffersVenueResponseModel]


class CollectiveOffersSubCategoryResponseModel(BaseModel):
    id: str
    label: str
    category: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, subcategory: subcategories_v2.Subcategory) -> "CollectiveOffersSubCategoryResponseModel":
        return cls(
            id=subcategory.id,
            label=subcategory.pro_label,
            category=subcategory.category.pro_label,
        )


class CollectiveOffersListSubCategoriesResponseModel(BaseModel):
    __root__: list[CollectiveOffersSubCategoryResponseModel]


class CollectiveOffersCategoryResponseModel(BaseModel):
    id: str
    name: str


class CollectiveOffersListCategoriesResponseModel(BaseModel):
    __root__: list[CollectiveOffersCategoryResponseModel]


class CollectiveOffersDomainResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CollectiveOffersListDomainsResponseModel(BaseModel):
    __root__: list[CollectiveOffersDomainResponseModel]


class CollectiveOffersStudentLevelResponseModel(BaseModel):
    id: str
    name: str


MAX_LIMIT_EDUCATIONAL_INSTITUTION = 20


class GetListEducationalInstitutionsQueryModel(BaseModel):
    id: int | None
    name: str | None
    institution_type: str | None
    city: str | None
    postal_code: str | None
    limit: int = MAX_LIMIT_EDUCATIONAL_INSTITUTION

    @validator("limit")
    def validate_limit(  # pylint: disable=no-self-argument
        cls: "GetListEducationalInstitutionsQueryModel", limit: int
    ) -> int:
        limit = min(limit, MAX_LIMIT_EDUCATIONAL_INSTITUTION)
        return limit

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOffersListStudentLevelsResponseModel(BaseModel):
    __root__: list[CollectiveOffersStudentLevelResponseModel]


class CollectiveOffersEducationalInstitutionResponseModel(BaseModel):
    id: int
    name: str
    institutionType: str
    city: str
    postalCode: str

    class Config:
        orm_mode = True


class CollectiveOffersListEducationalInstitutionResponseModel(BaseModel):
    __root__: list[CollectiveOffersEducationalInstitutionResponseModel]


class GetPublicCollectiveOfferResponseModel(BaseModel):
    id: int
    status: str
    name: str
    description: str | None
    subcategoryId: str
    bookingEmail: str | None
    contactEmail: str
    contactPhone: str
    domains: list[str]
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
    totalPrice: int
    numberOfTickets: int
    educationalPriceDetail: str | None
    educationalInstitution: str | None
    offerVenue: OfferVenueModel

    class Config:
        extra = "forbid"
        orm_mode = True

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "GetPublicCollectiveOfferResponseModel":
        return cls(
            id=offer.id,
            status=offer.status.name,  # type: ignore [attr-defined]
            name=offer.name,
            description=offer.description,
            subcategoryId=offer.subcategoryId,
            bookingEmail=offer.bookingEmail,
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            domains=[domain.name for domain in offer.domains],
            durationMinutes=offer.durationMinutes,
            interventionArea=offer.interventionArea,
            students=[student.value for student in offer.students],
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
            totalPrice=(offer.collectiveStock.price * 100),
            numberOfTickets=offer.collectiveStock.numberOfTickets,
            educationalPriceDetail=offer.collectiveStock.priceDetail,
            educationalInstitution=offer.institution.institutionId if offer.institutionId else None,
            offerVenue={
                "venueId": dehumanize(offer.offerVenue.get("venueId")) or None,
                "addressType": offer.offerVenue["addressType"],
                "otherAddress": offer.offerVenue["otherAddress"] or None,
            },
        )


class PostCollectiveOfferBodyModel(BaseModel):
    # offer part
    venue_id: int
    name: str
    description: str | None
    subcategory_id: str
    booking_email: str | None
    contact_email: str
    contact_phone: str
    domains: list[str]
    duration_minutes: int | None
    students: list[StudentLevels]
    audio_disability_compliant: bool = False
    mental_disability_compliant: bool = False
    motor_disability_compliant: bool = False
    visual_disability_compliant: bool = False
    offer_venue: OfferVenueModel
    intervention_area: list[str]
    # stock part
    beginning_datetime: datetime
    booking_limit_datetime: datetime
    total_price: int
    number_of_tickets: int
    price_detail: str | None
    # link to educational institution
    educational_institution_id: int | None

    _validate_number_of_tickets = number_of_tickets_validator("number_of_tickets")
    _validate_total_price = price_validator("total_price")
    _validate_beginning_datetime = beginning_datetime_validator("beginning_datetime")
    _validate_booking_limit_datetime = booking_limit_datetime_validator("booking_limit_datetime")
    _validate_price_detail = price_detail_validator("price_detail")

    @validator("name", pre=True)
    def validate_name(cls: BaseModel, name: str) -> str:  # pylint: disable=no-self-argument
        check_offer_name_length_is_valid(name)
        return name

    @validator("domains", pre=True)
    def validate_domains(  # pylint: disable=no-self-argument
        cls: "PostCollectiveOfferBodyModel",
        domains: list[str],
    ) -> list[str]:
        if len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchCollectiveOfferBodyModel(BaseModel):
    name: str | None
    description: str | None
    subcategoryId: str | None
    bookingEmail: str | None
    contactEmail: str | None
    contactPhone: str | None
    domains: list[str] | None
    students: list[StudentLevels] | None
    offerVenue: OfferVenueModel | None
    interventionArea: list[str] | None
    educationalPriceDetail: str | None
    durationMinutes: int | None
    # stock part
    beginningDatetime: datetime | None
    bookingLimitDatetime: datetime | None
    price: float | None = Field(alias="totalPrice")
    numberOfTickets: int | None
    priceDetail: str | None
    # educational_institution
    educationalInstitutionId: int | None

    _validate_number_of_tickets = number_of_tickets_validator("numberOfTickets")
    _validate_total_price = price_validator("price")
    _validate_educational_price_detail = price_detail_validator("educationalPriceDetail")
    _validate_beginning_datetime = beginning_datetime_validator("beginningDatetime")
    _validate_price_detail = price_detail_validator("priceDetail")

    @validator("domains")
    def validate_domains(  # pylint: disable=no-self-argument
        cls: "PatchCollectiveOfferBodyModel",
        domains: list[str],
    ) -> list[str]:
        if len(domains) == 0:
            raise ValueError("domains must have at least one value")

        return domains

    @validator("name", allow_reuse=True)
    def validate_name(  # pylint: disable=no-self-argument
        cls: "PatchCollectiveOfferBodyModel", name: str | None
    ) -> str | None:
        assert name is not None and name.strip() != ""
        check_offer_name_length_is_valid(name)
        return name

    @validator("domains")
    def validate_domains_collective_offer_edition(  # pylint: disable=no-self-argument
        cls: "PatchCollectiveOfferBodyModel",
        domains: list[int] | None,
    ) -> list[int] | None:
        if domains is None or (domains is not None and len(domains) == 0):
            raise ValueError("domains must have at least one value")

        return domains

    @validator("bookingLimitDatetime")
    def validate_booking_limit_datetime(  # pylint: disable=no-self-argument
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
    def validate_beginning_limit_datetime(  # pylint: disable=no-self-argument
        cls, beginningDatetime: datetime | None
    ) -> datetime | None:
        if beginningDatetime is None:
            raise ValueError("La date de début de l'événement ne peut pas être nulle.")
        return beginningDatetime

    class Config:
        alias_generator = to_camel
        extra = "forbid"
