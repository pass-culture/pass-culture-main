from datetime import datetime
import decimal
import typing
from typing import Iterable

from pydantic.v1 import PositiveInt
from pydantic.v1.fields import Field

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import schemas as educational_schemas
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers.utils import offer_app_link
from pcapi.routes.serialization import BaseModel


class MergeInstitutionPrebookingsQueryModel(educational_schemas.AdageBaseResponseModel):
    source_uai: str
    destination_uai: str
    bookings_ids: list[int]


class GetEducationalBookingsRequest(BaseModel):
    redactorEmail: str | None = Field(description="Email of querying redactor")

    class Config:
        title = "Prebookings query filters"


class EducationalBookingsResponse(educational_schemas.AdageBaseResponseModel):
    prebookings: list[educational_schemas.EducationalBookingResponse]

    class Config:
        title = "List of prebookings"


class EducationalBookingPerYearResponse(educational_schemas.AdageBaseResponseModel):
    id: int
    UAICode: str
    status: EducationalBookingStatus | CollectiveBookingStatus
    cancellationReason: CollectiveBookingCancellationReasons | None
    confirmationLimitDate: datetime
    totalAmount: decimal.Decimal
    startDatetime: datetime
    endDatetime: datetime
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
            cancellationReason=booking.cancellationReason,
            confirmationLimitDate=booking.confirmationLimitDate,
            totalAmount=booking.collectiveStock.price,
            startDatetime=booking.collectiveStock.startDatetime,
            endDatetime=booking.collectiveStock.endDatetime,
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


class EducationalBookingsPerYearResponse(educational_schemas.AdageBaseResponseModel):
    bookings: list[EducationalBookingPerYearResponse]


class GetAllBookingsPerYearQueryModel(BaseModel):
    page: PositiveInt | None
    per_page: PositiveInt | None


def serialize_collective_bookings(
    educational_bookings: list[CollectiveBooking],
) -> list[educational_schemas.EducationalBookingResponse]:
    serialized_educational_bookings = []
    for educational_booking in educational_bookings:
        serialized_educational_bookings.append(serialize_collective_booking(educational_booking))

    return serialized_educational_bookings


def serialize_collective_booking(
    collective_booking: CollectiveBooking,
) -> educational_schemas.EducationalBookingResponse:
    stock: educational_models.CollectiveStock = collective_booking.collectiveStock
    offer: educational_models.CollectiveOffer = stock.collectiveOffer
    domains = offer.domains
    venue: offerers_models.Venue = offer.venue
    return educational_schemas.EducationalBookingResponse(
        accessibility=_get_educational_offer_accessibility(offer),
        address=_get_collective_offer_address(offer),
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
        cancellationReason=collective_booking.cancellationReason,
        venueTimezone=venue.timezone,
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


def _get_collective_offer_contact(offer: educational_models.CollectiveOffer) -> educational_schemas.Contact:
    return educational_schemas.Contact(
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


def serialize_reimbursement_notification(
    collective_booking: CollectiveBooking, reason: str, value: decimal.Decimal, details: str
) -> educational_schemas.AdageReimbursementNotification:
    stock: educational_models.CollectiveStock = collective_booking.collectiveStock
    offer: educational_models.CollectiveOffer = stock.collectiveOffer
    domains = offer.domains
    venue: offerers_models.Venue = offer.venue
    return educational_schemas.AdageReimbursementNotification(
        accessibility=_get_educational_offer_accessibility(offer),
        address=_get_collective_offer_address(offer),
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        cancellationDate=collective_booking.cancellationDate,
        cancellationLimitDate=collective_booking.cancellationLimitDate,
        cancellationReason=collective_booking.cancellationReason,
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
        venueTimezone=venue.timezone,
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
