import decimal
from typing import Iterable

from pcapi.core.educational import models
from pcapi.core.educational import schemas
from pcapi.core.educational.serialization.collective_offer import get_collective_offer_address


def get_collective_bookings_per_year_response(
    bookings: Iterable[models.CollectiveBooking],
) -> schemas.EducationalBookingsPerYearResponse:
    serialized_bookings: list[schemas.EducationalBookingPerYearResponse] = []

    for booking in bookings:
        stock = booking.collectiveStock
        offer = stock.collectiveOffer

        serialized_bookings.append(
            schemas.EducationalBookingPerYearResponse(
                id=booking.id,
                UAICode=booking.educationalInstitution.institutionId,
                status=get_collective_booking_status(booking),
                additionalDetails=offer.additionalDetails,
                cancellationReason=booking.cancellationReason,
                confirmationDate=booking.confirmationDate,
                confirmationLimitDate=booking.confirmationLimitDate,
                numberOfTickets=stock.numberOfTickets,
                numberOfTeachers=stock.numberOfTeachers,
                price=stock.price,
                servicePrice=stock.servicePrice,
                additionalFees=[schemas.AdditionalFeeResponse.build(fee) for fee in stock.collectiveAdditionalFees],
                startDatetime=stock.startDatetime,
                endDatetime=stock.endDatetime,
                venueTimezone=offer.venue.offererAddress.address.timezone,
                name=offer.name,
                redactorEmail=booking.educationalRedactor.email,
                domainIds=[domain.id for domain in offer.domains],
                domainLabels=[domain.name for domain in offer.domains],
                venueId=offer.venueId,
                venueName=offer.venue.name,
                offererName=offer.venue.managingOfferer.name,
                formats=offer.formats,
            )
        )

    return schemas.EducationalBookingsPerYearResponse(bookings=serialized_bookings)


def serialize_collective_bookings(
    educational_bookings: list[models.CollectiveBooking],
) -> list[schemas.EducationalBookingResponse]:
    serialized_educational_bookings = []
    for educational_booking in educational_bookings:
        serialized_educational_bookings.append(serialize_collective_booking(educational_booking))

    return serialized_educational_bookings


def serialize_collective_booking(
    collective_booking: models.CollectiveBooking,
) -> schemas.EducationalBookingResponse:
    stock = collective_booking.collectiveStock
    offer = stock.collectiveOffer
    domains = offer.domains
    venue = offer.venue
    redactor = collective_booking.educationalRedactor

    return schemas.EducationalBookingResponse(
        accessibility=_get_educational_offer_accessibility(offer),
        address=get_collective_offer_address(offer),
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        cancellationDate=collective_booking.cancellationDate,
        cancellationLimitDate=collective_booking.cancellationLimitDate,
        confirmationDate=collective_booking.confirmationDate,
        confirmationLimitDate=collective_booking.confirmationLimitDate,
        contact=_get_collective_offer_contact(offer),
        creationDate=collective_booking.dateCreated,
        description=offer.description,
        additionalDetails=offer.additionalDetails,
        durationMinutes=offer.durationMinutes,
        id=collective_booking.id,
        venueName=venue.publicName or venue.name,
        name=offer.name,
        numberOfTickets=stock.numberOfTickets,
        numberOfTeachers=stock.numberOfTeachers,
        participants=[student.value for student in offer.students],
        priceDetail=stock.priceDetail,
        price=stock.price,
        servicePrice=stock.servicePrice,
        additionalFees=[schemas.AdditionalFeeResponse.build(fee) for fee in stock.collectiveAdditionalFees],
        redactor=schemas.Redactor(
            email=redactor.email,
            redactorFirstName=redactor.firstName,
            redactorLastName=redactor.lastName,
            redactorCivility=redactor.civility,
        ),
        UAICode=collective_booking.educationalInstitution.institutionId,
        yearId=int(collective_booking.educationalYearId),
        status=get_collective_booking_status(collective_booking),
        cancellationReason=collective_booking.cancellationReason,
        venueTimezone=venue.offererAddress.address.timezone,
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
    collective_booking: models.CollectiveBooking,
) -> models.CollectiveBookingStatus | schemas.CollectiveBookingRefused:
    if collective_booking.status in (
        models.CollectiveBookingStatus.USED,
        models.CollectiveBookingStatus.REIMBURSED,
    ):
        return models.CollectiveBookingStatus.USED

    if collective_booking.cancellationReason in [
        models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE,
        models.CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER,
    ]:
        return "REFUSED"

    return collective_booking.status


def _get_collective_offer_contact(offer: models.CollectiveOffer) -> schemas.Contact:
    return schemas.Contact(
        email=offer.contactEmail,
        phone=offer.contactPhone,
    )


def _get_educational_offer_accessibility(offer: models.CollectiveOffer) -> str:
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
    collective_booking: models.CollectiveBooking, reason: str, value: decimal.Decimal, details: str
) -> schemas.AdageReimbursementNotification:
    return schemas.AdageReimbursementNotification(
        **serialize_collective_booking(collective_booking).dict(),
        reimbursementReason=reason,
        reimbursedValue=value,
        reimbursementDetails=details,
    )
