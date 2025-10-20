import decimal
from typing import Iterable

from pcapi.core.educational import models as educational_models
from pcapi.core.educational import schemas as educational_schemas
from pcapi.core.educational.adage_backends import serialize as adage_serialize
from pcapi.core.offers.utils import offer_app_link


def get_collective_bookings_per_year_response(
    bookings: Iterable[educational_models.CollectiveBooking],
) -> educational_schemas.EducationalBookingsPerYearResponse:
    serialized_bookings = [
        educational_schemas.EducationalBookingPerYearResponse(
            id=booking.id,
            UAICode=booking.educationalInstitution.institutionId,
            status=get_collective_booking_status(booking),  # type: ignore[arg-type]
            cancellationReason=booking.cancellationReason,
            confirmationLimitDate=booking.confirmationLimitDate,
            totalAmount=booking.collectiveStock.price,
            startDatetime=booking.collectiveStock.startDatetime,
            endDatetime=booking.collectiveStock.endDatetime,
            venueTimezone=booking.collectiveStock.collectiveOffer.venue.offererAddress.address.timezone,
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
    return educational_schemas.EducationalBookingsPerYearResponse(bookings=serialized_bookings)


def serialize_collective_bookings(
    educational_bookings: list[educational_models.CollectiveBooking],
) -> list[educational_schemas.EducationalBookingResponse]:
    serialized_educational_bookings = []
    for educational_booking in educational_bookings:
        serialized_educational_bookings.append(serialize_collective_booking(educational_booking))

    return serialized_educational_bookings


def serialize_collective_booking(
    collective_booking: educational_models.CollectiveBooking,
) -> educational_schemas.EducationalBookingResponse:
    stock = collective_booking.collectiveStock
    offer = stock.collectiveOffer
    domains = offer.domains
    venue = offer.venue

    return educational_schemas.EducationalBookingResponse(
        accessibility=_get_educational_offer_accessibility(offer),
        address=adage_serialize.get_collective_offer_address(offer),
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        cancellationDate=collective_booking.cancellationDate,
        cancellationLimitDate=collective_booking.cancellationLimitDate,
        confirmationDate=collective_booking.confirmationDate,
        confirmationLimitDate=collective_booking.confirmationLimitDate,
        contact=_get_collective_offer_contact(offer),
        creationDate=collective_booking.dateCreated,
        description=offer.description,
        durationMinutes=offer.durationMinutes,
        expirationDate=None,
        id=collective_booking.id,
        hasUrl=False,
        venueName=venue.publicName or venue.name,
        name=offer.name,
        numberOfTickets=stock.numberOfTickets,
        participants=[student.value for student in offer.students],
        priceDetail=stock.priceDetail,
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
        venueTimezone=venue.offererAddress.address.timezone,
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
    collective_booking: educational_models.CollectiveBooking,
) -> str:
    if collective_booking.status in (
        educational_models.CollectiveBookingStatus.USED,
        educational_models.CollectiveBookingStatus.REIMBURSED,
    ):
        return educational_models.CollectiveBookingStatus.USED.value

    if collective_booking.cancellationReason in [
        educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE,
        educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER,
    ]:
        return "REFUSED"

    return collective_booking.status.value


def _get_collective_offer_contact(offer: educational_models.CollectiveOffer) -> educational_schemas.Contact:
    return educational_schemas.Contact(
        email=offer.contactEmail,
        phone=offer.contactPhone,
    )


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
    collective_booking: educational_models.CollectiveBooking, reason: str, value: decimal.Decimal, details: str
) -> educational_schemas.AdageReimbursementNotification:
    stock = collective_booking.collectiveStock
    offer = stock.collectiveOffer
    domains = offer.domains
    venue = offer.venue

    return educational_schemas.AdageReimbursementNotification(
        accessibility=_get_educational_offer_accessibility(offer),
        address=adage_serialize.get_collective_offer_address(offer),
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        cancellationDate=collective_booking.cancellationDate,
        cancellationLimitDate=collective_booking.cancellationLimitDate,
        cancellationReason=collective_booking.cancellationReason,
        confirmationDate=collective_booking.confirmationDate,
        confirmationLimitDate=collective_booking.confirmationLimitDate,
        contact=_get_collective_offer_contact(offer),
        creationDate=collective_booking.dateCreated,
        description=offer.description,
        durationMinutes=offer.durationMinutes,
        expirationDate=None,
        id=collective_booking.id,
        hasUrl=False,
        venueName=venue.publicName or venue.name,
        name=offer.name,
        numberOfTickets=stock.numberOfTickets,
        participants=[student.value for student in offer.students],
        priceDetail=stock.priceDetail,
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
        venueTimezone=venue.offererAddress.address.timezone,
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
        formats=collective_booking.collectiveStock.collectiveOffer.formats,
    )
