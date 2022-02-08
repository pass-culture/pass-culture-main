from datetime import datetime
from typing import Optional
from typing import Union

from pydantic.fields import Field

from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.utils import offer_app_link
from pcapi.routes.adage.v1.serialization.config import AdageBaseResponseModel
from pcapi.routes.native.v1.serialization.common_models import Coordinates
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class GetEducationalBookingsRequest(BaseModel):
    redactorEmail: Optional[str] = Field(description="Email of querying redactor")
    status: Optional[Union[EducationalBookingStatus, BookingStatus]] = Field(
        description="Status of retrieved preboookings"
    )

    class Config:
        title = "Prebookings query filters"


class Redactor(AdageBaseResponseModel):
    email: str
    redactorFirstName: Optional[str]
    redactorLastName: Optional[str]
    redactorCivility: Optional[str]

    class Config:
        alias_generator = to_camel


class Contact(AdageBaseResponseModel):
    email: Optional[str]
    phone: Optional[str]


class EducationalBookingResponse(AdageBaseResponseModel):
    accessibility: str = Field(description="Accessibility of the offer")
    address: str = Field(description="Adresse of event")
    beginningDatetime: datetime = Field(description="Beginnning date of event")
    cancellationDate: Optional[datetime] = Field(description="Date of cancellation if prebooking is cancelled")
    cancellationLimitDate: Optional[datetime] = Field(description="Limit date to cancel the prebooking")
    city: str
    confirmationDate: Optional[datetime] = Field(description="Date of confirmation if prebooking is confirmed")
    confirmationLimitDate: datetime = Field(description="Limit date to confirm the prebooking")
    contact: Contact = Field(description="Contact of the prebooking")
    coordinates: Coordinates
    creationDate: datetime
    description: Optional[str] = Field(description="Offer description")
    durationMinutes: Optional[int] = Field(description="Offer's duration in minutes")
    expirationDate: Optional[datetime] = Field(description="Expiration date after which booking is cancelled")
    id: int = Field(description="pass Culture's prebooking id")
    isDigital: bool = Field(description="If true the event is accessed digitally")
    venueName: str = Field(description="Name of cultural venue proposing the event")
    name: str = Field(description="Name of event")
    numberOfTickets: Optional[int] = Field(description="Number of tickets")
    postalCode: str
    price: float
    quantity: int = Field(description="Number of place prebooked")
    redactor: Redactor
    UAICode: str = Field(description="Educational institution UAI code")
    yearId: int = Field(description="Shared year id")
    status: Union[EducationalBookingStatus, BookingStatus]
    participants: list[str] = Field(description="List of class levels which can participate")
    priceDetail: Optional[str] = Field(description="Offer's stock price detail")
    venueTimezone: str
    subcategoryLabel: str = Field(description="Subcategory label")
    totalAmount: float = Field(description="Total price of the prebooking")
    url: Optional[str] = Field(description="Url to access the offer")
    withdrawalDetails: Optional[str]

    class Config:
        title = "Prebooking detailed response"
        alias_generator = to_camel
        allow_population_by_field_name = True


class EducationalBookingsResponse(AdageBaseResponseModel):
    prebookings: list[EducationalBookingResponse]

    class Config:
        title = "List of prebookings"


class EducationalBookingPerYearResponse(AdageBaseResponseModel):
    id: int
    UAICode: str
    status: Union[EducationalBookingStatus, BookingStatus]
    confirmationLimitDate: datetime
    totalAmount: float
    beginningDatetime: datetime
    venueTimezone: str
    name: str
    redactorEmail: str


class EducationalBookingsPerYearResponse(AdageBaseResponseModel):
    bookings: list[EducationalBookingPerYearResponse]


class EducationalBookingEdition(EducationalBookingResponse):
    updatedFields: list[str] = Field(description="List of fields updated")


def serialize_educational_bookings(educational_bookings: list[EducationalBooking]) -> list[EducationalBookingResponse]:
    serialized_educational_bookings = []
    for educational_booking in educational_bookings:
        serialized_educational_bookings.append(serialize_educational_booking(educational_booking))

    return serialized_educational_bookings


def serialize_educational_booking(educational_booking: EducationalBooking) -> EducationalBookingResponse:
    booking = educational_booking.booking
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    return EducationalBookingResponse(
        accessibility=_get_educational_offer_accessibility(offer),
        address=_get_educational_offer_address(offer),
        beginningDatetime=stock.beginningDatetime,
        cancellationDate=booking.cancellationDate,
        cancellationLimitDate=booking.cancellationLimitDate,
        city=venue.city,
        confirmationDate=educational_booking.confirmationDate,
        confirmationLimitDate=educational_booking.confirmationLimitDate,
        contact=_get_educational_offer_contact(offer),
        coordinates={
            "latitude": venue.latitude,
            "longitude": venue.longitude,
        },
        creationDate=booking.dateCreated,
        description=offer.description,
        durationMinutes=offer.durationMinutes,
        expirationDate=booking.expirationDate,
        id=educational_booking.id,
        isDigital=offer.isDigital,
        venueName=venue.name,
        name=offer.name,
        numberOfTickets=stock.numberOfTickets,
        participants=offer.extraData.get("students", []) if offer.extraData is not None else [],
        priceDetail=stock.educationalPriceDetail,
        postalCode=venue.postalCode,
        price=booking.amount,
        quantity=booking.quantity,
        redactor={
            "email": educational_booking.educationalRedactor.email,
            "redactorFirstName": educational_booking.educationalRedactor.firstName,
            "redactorLastName": educational_booking.educationalRedactor.lastName,
            "redactorCivility": educational_booking.educationalRedactor.civility,
        },
        UAICode=educational_booking.educationalInstitution.institutionId,
        yearId=educational_booking.educationalYearId,
        status=get_educational_booking_status(educational_booking),
        venueTimezone=venue.timezone,
        subcategoryLabel=offer.subcategory.app_label,
        totalAmount=booking.total_amount,
        url=offer_app_link(offer),
        withdrawalDetails=offer.withdrawalDetails,
    )


def get_educational_booking_status(
    educational_booking: EducationalBooking,
) -> Union[EducationalBookingStatus, BookingStatus]:
    if (
        educational_booking.booking.status == BookingStatus.USED
        or educational_booking.booking.status == BookingStatus.REIMBURSED
    ):
        return BookingStatus.USED.value

    # This is to return REFUSED instead of CANCELLED if educational booking is REFUSED
    if educational_booking.status is not None:
        return educational_booking.status.value

    return educational_booking.booking.status.value


def _get_educational_offer_contact(offer: offers_models.Offer) -> Contact:
    if offer.extraData is None:
        return Contact(email=None, phone=None)

    return Contact(
        email=offer.extraData.get("contactEmail", None),
        phone=offer.extraData.get("contactPhone", None),
    )


def _get_educational_offer_address(offer: offers_models.Offer) -> str:
    default_address = f"{offer.venue.address}, {offer.venue.postalCode} {offer.venue.city}"
    if offer.extraData is None or offer.extraData.get("offerVenue", None) is None:
        return default_address

    address_type = offer.extraData["offerVenue"]["addressType"]

    if address_type == "offererVenue":
        return default_address

    if address_type == "other":
        return offer.extraData["offerVenue"]["otherAddress"]

    if address_type == "school":
        return "Dans l’établissement scolaire"

    return default_address


def _get_educational_offer_accessibility(offer: offers_models.Offer) -> str:
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
