from datetime import datetime
import decimal
import typing
from typing import Iterable

from pydantic.v1 import PositiveInt
from pydantic.v1.fields import Field

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers.utils import offer_app_link
from pcapi.routes.adage.v1.serialization.config import AdageBaseResponseModel
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class MergeInstitutionPrebookingsQueryModel(AdageBaseResponseModel):
    source_uai: str
    destination_uai: str
    bookings_ids: list[int]


class GetEducationalBookingsRequest(BaseModel):
    redactorEmail: str | None = Field(description="Email of querying redactor")

    class Config:
        title = "Prebookings query filters"


class Redactor(AdageBaseResponseModel):
    email: str
    redactorFirstName: str | None
    redactorLastName: str | None
    redactorCivility: str | None

    class Config:
        alias_generator = to_camel


class Contact(AdageBaseResponseModel):
    email: str | None
    phone: str | None


class EducationalBookingBaseResponse(AdageBaseResponseModel):
    accessibility: str = Field(description="Accessibility of the offer")
    address: str = Field(description="Adresse of event")
    beginningDatetime: datetime = Field(description="Beginnning date of event")
    startDatetime: datetime = Field(description="Start date of event")
    endDatetime: datetime = Field(description="End date of event")
    cancellationDate: datetime | None = Field(description="Date of cancellation if prebooking is cancelled")
    cancellationLimitDate: datetime | None = Field(description="Limit date to cancel the prebooking")
    city: str | None
    confirmationDate: datetime | None = Field(description="Date of confirmation if prebooking is confirmed")
    confirmationLimitDate: datetime = Field(description="Limit date to confirm the prebooking")
    contact: Contact = Field(description="Contact of the prebooking")
    coordinates: Coordinates
    creationDate: datetime
    description: str | None = Field(description="Offer description")
    durationMinutes: int | None = Field(description="Offer's duration in minutes")
    expirationDate: datetime | None = Field(description="Expiration date after which booking is cancelled")
    id: int = Field(description="pass Culture's prebooking id")
    isDigital: bool = Field(description="If true the event is accessed digitally")
    venueName: str = Field(description="Name of cultural venue proposing the event")
    name: str = Field(description="Name of event")
    numberOfTickets: int | None = Field(description="Number of tickets")
    postalCode: str | None
    price: decimal.Decimal
    quantity: int = Field(description="Number of place prebooked")
    redactor: Redactor
    UAICode: str = Field(description="Educational institution UAI code")
    yearId: int = Field(description="Shared year id")
    status: EducationalBookingStatus | CollectiveBookingStatus
    participants: list[str] = Field(description="List of class levels which can participate")
    priceDetail: str | None = Field(description="Offer's stock price detail")
    venueTimezone: str
    subcategoryLabel: str = Field(description="Subcategory label")
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

    class Config:
        title = "Prebooking detailed response"
        alias_generator = to_camel
        allow_population_by_field_name = True


class EducationalBookingResponse(EducationalBookingBaseResponse):
    formats: list[subcategories.EacFormat] | None


class EducationalBookingsResponse(AdageBaseResponseModel):
    prebookings: list[EducationalBookingResponse]

    class Config:
        title = "List of prebookings"


class EducationalBookingPerYearResponse(AdageBaseResponseModel):
    id: int
    UAICode: str
    status: EducationalBookingStatus | CollectiveBookingStatus
    confirmationLimitDate: datetime
    totalAmount: decimal.Decimal
    beginningDatetime: datetime
    venueTimezone: str
    name: str
    redactorEmail: str
    domainIds: list[int]
    domainLabels: list[str]
    venueId: int | None
    venueName: str | None
    offererName: str | None
    formats: typing.Sequence[subcategories.EacFormat] | None

    class Config:
        use_enum_values = True


def get_collective_bookings_per_year_response(
    bookings: Iterable[CollectiveBooking],
) -> "EducationalBookingsPerYearResponse":
    serialized_bookings = [
        EducationalBookingPerYearResponse(
            id=booking.id,
            UAICode=booking.educationalInstitution.institutionId,
            status=get_collective_booking_status(booking),  # type: ignore[arg-type]
            confirmationLimitDate=booking.confirmationLimitDate,
            totalAmount=booking.collectiveStock.price,
            beginningDatetime=booking.collectiveStock.beginningDatetime,
            venueTimezone=booking.collectiveStock.collectiveOffer.venue.timezone,
            name=booking.collectiveStock.collectiveOffer.name,
            redactorEmail=booking.educationalRedactor.email,
            domainIds=[domain.id for domain in booking.collectiveStock.collectiveOffer.domains],
            domainLabels=[domain.name for domain in booking.collectiveStock.collectiveOffer.domains],
            venueId=booking.collectiveStock.collectiveOffer.venueId,
            venueName=booking.collectiveStock.collectiveOffer.venue.name,
            offererName=booking.collectiveStock.collectiveOffer.venue.managingOfferer.name,
            formats=booking.collectiveStock.collectiveOffer.formats,
        )
        for booking in bookings
    ]
    return EducationalBookingsPerYearResponse(bookings=serialized_bookings)


class EducationalBookingsPerYearResponse(AdageBaseResponseModel):
    bookings: list[EducationalBookingPerYearResponse]


class GetAllBookingsPerYearQueryModel(BaseModel):
    page: PositiveInt | None
    per_page: PositiveInt | None


class EducationalBookingEdition(EducationalBookingResponse):
    updatedFields: list[str] = Field(description="List of fields updated")


def serialize_collective_bookings(educational_bookings: list[CollectiveBooking]) -> list[EducationalBookingResponse]:
    serialized_educational_bookings = []
    for educational_booking in educational_bookings:
        serialized_educational_bookings.append(serialize_collective_booking(educational_booking))

    return serialized_educational_bookings


def serialize_collective_booking(collective_booking: CollectiveBooking) -> EducationalBookingResponse:
    stock: educational_models.CollectiveStock = collective_booking.collectiveStock
    offer: educational_models.CollectiveOffer = stock.collectiveOffer
    domains = offer.domains
    venue: offerers_models.Venue = offer.venue
    return EducationalBookingResponse(
        accessibility=_get_educational_offer_accessibility(offer),
        address=_get_collective_offer_address(offer),
        beginningDatetime=stock.beginningDatetime,
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        cancellationDate=collective_booking.cancellationDate,
        cancellationLimitDate=collective_booking.cancellationLimitDate,
        city=venue.city,
        confirmationDate=collective_booking.confirmationDate,
        confirmationLimitDate=collective_booking.confirmationLimitDate,
        contact=_get_collective_offer_contact(offer),
        coordinates={  # type: ignore[arg-type]
            "latitude": venue.latitude,
            "longitude": venue.longitude,
        },
        creationDate=collective_booking.dateCreated,
        description=offer.description,
        durationMinutes=offer.durationMinutes,
        expirationDate=None,
        id=collective_booking.id,
        isDigital=False,
        venueName=venue.publicName or venue.name,
        name=offer.name,
        numberOfTickets=stock.numberOfTickets,
        participants=[student.value for student in offer.students],
        priceDetail=stock.priceDetail,
        postalCode=venue.postalCode,
        price=stock.price,
        quantity=1,
        redactor={  # type: ignore[arg-type]
            "email": collective_booking.educationalRedactor.email,
            "redactorFirstName": collective_booking.educationalRedactor.firstName,
            "redactorLastName": collective_booking.educationalRedactor.lastName,
            "redactorCivility": collective_booking.educationalRedactor.civility,
        },
        UAICode=collective_booking.educationalInstitution.institutionId,
        yearId=collective_booking.educationalYearId,  # type: ignore[arg-type]
        status=get_collective_booking_status(collective_booking),  # type: ignore[arg-type]
        venueTimezone=venue.timezone,  # type: ignore[arg-type]
        subcategoryLabel=offer.subcategory.app_label if offer.subcategory else "",
        totalAmount=stock.price,
        url=offer_app_link(offer),
        withdrawalDetails=None,
        domain_ids=[domain.id for domain in domains],
        domain_labels=[domain.name for domain in domains],
        interventionArea=offer.interventionArea,
        imageCredit=offer.imageCredit,
        imageUrl=offer.imageUrl,
        venueId=venue.id,
        offererName=venue.managingOfferer.name,
        formats=offer.formats,
    )


def get_collective_booking_status(
    collective_booking: CollectiveBooking,
) -> str:
    if collective_booking.status in (
        CollectiveBookingStatus.USED,
        CollectiveBookingStatus.REIMBURSED,
    ):
        return CollectiveBookingStatus.USED.value

    if collective_booking.cancellationReason in [
        CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE,
        CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER,
    ]:
        return "REFUSED"

    return collective_booking.status.value


def _get_collective_offer_contact(offer: educational_models.CollectiveOffer) -> Contact:
    return Contact(
        email=offer.contactEmail,
        phone=offer.contactPhone,
    )


def _get_collective_offer_address(offer: educational_models.CollectiveOffer) -> str:
    default_address = f"{offer.venue.street}, {offer.venue.postalCode} {offer.venue.city}"

    if offer.offerVenue is None:
        return default_address

    address_type = offer.offerVenue["addressType"]

    if address_type == "offererVenue":
        return default_address

    if address_type == "other":
        return offer.offerVenue["otherAddress"]

    if address_type == "school":
        return "Dans l’établissement scolaire"

    return default_address


def _get_educational_offer_accessibility(offer: educational_models.CollectiveOffer) -> str:
    disability_compliance = []
    if offer.audioDisabilityCompliant:
        disability_compliance.append("Auditif")
    if offer.mentalDisabilityCompliant:
        disability_compliance.append("Psychique ou cognitif")
    if offer.motorDisabilityCompliant:
        disability_compliance.append("Moteur")
    if offer.visualDisabilityCompliant:
        disability_compliance.append("Visuel")

    return ", ".join(disability_compliance) or "Non accessible"


class AdageReimbursementNotification(EducationalBookingBaseResponse):
    reimbursementReason: str
    reimbursedValue: decimal.Decimal
    reimbursementDetails: str


def serialize_reimbursement_notification(
    collective_booking: CollectiveBooking, reason: str, value: decimal.Decimal, details: str
) -> AdageReimbursementNotification:
    stock: educational_models.CollectiveStock = collective_booking.collectiveStock
    offer: educational_models.CollectiveOffer = stock.collectiveOffer
    domains = offer.domains
    venue: offerers_models.Venue = offer.venue
    return AdageReimbursementNotification(
        accessibility=_get_educational_offer_accessibility(offer),
        address=_get_collective_offer_address(offer),
        beginningDatetime=stock.beginningDatetime,
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        cancellationDate=collective_booking.cancellationDate,
        cancellationLimitDate=collective_booking.cancellationLimitDate,
        city=venue.city,
        confirmationDate=collective_booking.confirmationDate,
        confirmationLimitDate=collective_booking.confirmationLimitDate,
        contact=_get_collective_offer_contact(offer),
        coordinates={  # type: ignore[arg-type]
            "latitude": venue.latitude,
            "longitude": venue.longitude,
        },
        creationDate=collective_booking.dateCreated,
        description=offer.description,
        durationMinutes=offer.durationMinutes,
        expirationDate=None,
        id=collective_booking.id,
        isDigital=False,
        venueName=venue.publicName or venue.name,
        name=offer.name,
        numberOfTickets=stock.numberOfTickets,
        participants=[student.value for student in offer.students],
        priceDetail=stock.priceDetail,
        postalCode=venue.postalCode,
        price=stock.price,
        quantity=1,
        redactor={  # type: ignore[arg-type]
            "email": collective_booking.educationalRedactor.email,
            "redactorFirstName": collective_booking.educationalRedactor.firstName,
            "redactorLastName": collective_booking.educationalRedactor.lastName,
            "redactorCivility": collective_booking.educationalRedactor.civility,
        },
        UAICode=collective_booking.educationalInstitution.institutionId,
        yearId=collective_booking.educationalYearId,  # type: ignore[arg-type]
        status=get_collective_booking_status(collective_booking),  # type: ignore[arg-type]
        venueTimezone=venue.timezone,  # type: ignore[arg-type]
        subcategoryLabel=offer.subcategory.app_label if offer.subcategory else "",
        totalAmount=stock.price,
        url=offer_app_link(offer),
        withdrawalDetails=None,
        domain_ids=[domain.id for domain in domains],
        domain_labels=[domain.name for domain in domains],
        interventionArea=offer.interventionArea,
        imageCredit=offer.imageCredit,
        imageUrl=offer.imageUrl,
        reimbursementReason=reason,
        reimbursedValue=value,
        reimbursementDetails=details,
        venueId=venue.id,
        offererName=venue.managingOfferer.name,
    )
