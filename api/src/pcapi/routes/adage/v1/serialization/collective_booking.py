import datetime
import typing

import pydantic

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models
from pcapi.core.educational import schemas
from pcapi.core.educational.serialization.collective_booking import get_collective_booking_status
from pcapi.routes.serialization import HttpBodyModel


class EducationalBookingPerYearResponse(HttpBodyModel):
    id: int
    UAICode: str
    status: models.CollectiveBookingStatus | schemas.CollectiveBookingRefused
    additionalDetails: str | None
    cancellationReason: models.CollectiveBookingCancellationReasons | None
    confirmationDate: datetime.datetime | None
    confirmationLimitDate: datetime.datetime
    numberOfTickets: int
    numberOfTeachers: int
    price: float
    servicePrice: float
    additionalFees: list[schemas.AdditionalFeeResponseV2]
    startDatetime: datetime.datetime
    endDatetime: datetime.datetime
    venueTimezone: str
    name: str
    redactorEmail: str
    domainIds: list[int]
    domainLabels: list[str]
    venueId: int
    venueName: str
    offererName: str
    formats: list[EacFormat]

    model_config = pydantic.ConfigDict(use_enum_values=True, alias_generator=None)

    @classmethod
    def build(cls, booking: models.CollectiveBooking) -> typing.Self:
        stock = booking.collectiveStock
        offer = stock.collectiveOffer

        return cls(
            id=booking.id,
            UAICode=booking.educationalInstitution.institutionId,
            status=get_collective_booking_status(booking),
            additionalDetails=offer.additionalDetails,
            cancellationReason=booking.cancellationReason,
            confirmationDate=booking.confirmationDate,
            confirmationLimitDate=booking.confirmationLimitDate,
            numberOfTickets=stock.numberOfTickets,
            numberOfTeachers=stock.numberOfTeachers,
            price=float(stock.price),
            servicePrice=float(stock.servicePrice),
            additionalFees=[schemas.AdditionalFeeResponseV2.build(fee) for fee in stock.collectiveAdditionalFees],
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


class EducationalBookingsPerYearResponse(HttpBodyModel):
    bookings: list[EducationalBookingPerYearResponse]
