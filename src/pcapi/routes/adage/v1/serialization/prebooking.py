from datetime import datetime
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic.fields import Field

from pcapi import settings
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.native.v1.serialization.offers import OfferCategoryResponse
from pcapi.routes.native.v1.serialization.offers import OfferImageResponse
from pcapi.routes.native.v1.serialization.offers import get_serialized_offer_category
from pcapi.serialization.utils import to_camel
from pcapi.utils.human_ids import humanize


class GetPreBookingsRequest(BaseModel):
    redactorEmail: Optional[str] = Field(description="Email of querying redactor")
    status: Optional[Union[EducationalBookingStatus, BookingStatus]] = Field(
        description="Status of retrieved preboookings"
    )

    class Config:
        title = "Prebookings query filters"


class Redactor(BaseModel):
    email: str
    redactorFirstName: str
    redactorLastName: str
    redactorCivility: str

    class Config:
        alias_generator = to_camel


class PreBookingResponse(BaseModel):
    address: str = Field(description="Adresse of event")
    beginningDatetime: datetime = Field(description="Beginnning date of event")
    cancellationDate: Optional[datetime] = Field(description="Date of cancellation if prebooking is cancelled")
    cancellationLimitDate: Optional[datetime] = Field(description="Limit date to cancel the prebooking")
    category: OfferCategoryResponse
    city: str
    confirmationDate: Optional[datetime] = Field(description="Date of confirmation if prebooking is confirmed")
    confirmationLimitDate: datetime = Field(description="Limit date to confirm the prebooking")
    coordinates: Coordinates
    creationDate: datetime
    description: str = Field(description="Offer description")
    durationMinutes: Optional[int] = Field(description="Offer's duration in minutes")
    expirationDate: Optional[datetime] = Field(description="Expiration date after which booking is cancelled")
    id: int = Field(description="pass Culture's prebooking id")
    image: Optional[OfferImageResponse]
    isDigital: bool = Field(description="If true the event is accessed digitally")
    venueName: str = Field(description="Name of cultural venue proposing the event")
    name: str = Field(description="Name of event")
    postalCode: str
    price: float
    quantity: int = Field(description="Number of place prebooked")
    redactor: Redactor
    UAICode: str = Field(description="Educational institution UAI code")
    yearId: int = Field(description="Shared year id")
    status: Union[EducationalBookingStatus, BookingStatus]
    venueTimezone: str
    totalAmount: float = Field(description="Total price of the prebooking")
    url: Optional[str] = Field(description="Url to access the offer")
    withdrawalDetails: Optional[str]

    class Config:
        title = "Prebooking detailed response"
        alias_generator = to_camel
        allow_population_by_field_name = True


class PreBookingsResponse(BaseModel):
    prebookings: list[PreBookingResponse]

    class Config:
        title = "List of prebookings"


def get_prebookings_serialized(bookings: list[Booking]) -> list[PreBookingResponse]:
    prebookings = []
    for booking in bookings:
        stock = booking.stock
        offer = stock.offer
        venue = offer.venue
        user = booking.user
        prebooking_response = PreBookingResponse(
            address=venue.address,
            beginningDatetime=stock.beginningDatetime,
            cancellationDate=booking.cancellationDate,
            cancellationLimitDate=booking.cancellationLimitDate,
            category=get_serialized_offer_category(offer),
            city=venue.city,
            confirmationDate=booking.educationalBooking.confirmationDate,
            confirmationLimitDate=booking.educationalBooking.confirmationLimitDate,
            coordinates={
                "latitude": venue.latitude,
                "longitude": venue.longitude,
            },
            creationDate=booking.dateCreated,
            description=offer.description,
            durationMinutes=offer.durationMinutes,
            expirationDate=booking.expirationDate,
            id=booking.educationalBooking.id,
            image={"url": offer.image.url, "credit": offer.image.credit} if offer.image else None,
            isDigital=offer.isDigital,
            venueName=venue.name,
            name=offer.name,
            postalCode=venue.postalCode,
            price=booking.amount,
            quantity=booking.quantity,
            redactor={
                "email": user.email,
                "redactorFirstName": user.firstName,
                "redactorLastName": user.lastName,
                "redactorCivility": user.civility,
            },
            UAICode=booking.educationalBooking.educationalInstitution.institutionId,
            yearId=booking.educationalBooking.educationalYearId,
            status=get_education_booking_status(booking),
            venueTimezone=venue.timezone,
            totalAmount=booking.amount * booking.quantity,
            url=f"{settings.WEBAPP_URL}/accueil/details/{humanize(offer.id)}",
            withdrawalDetails=offer.withdrawalDetails,
        )
        prebookings.append(prebooking_response)

    return prebookings


def get_education_booking_status(booking: Booking) -> Union[EducationalBookingStatus, BookingStatus]:
    if booking.educationalBooking.status and not booking.status == BookingStatus.USED:
        return booking.educationalBooking.status.value

    return booking.status.value
