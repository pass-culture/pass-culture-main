from pcapi.core.educational import models
from pcapi.core.educational.serialization.collective_booking import _get_educational_offer_accessibility
from pcapi.core.offers.utils import offer_app_link
from pcapi.utils.date import format_into_utc_date


def expected_serialized_prebooking(booking: models.CollectiveBooking) -> dict:
    stock = booking.collectiveStock
    offer = stock.collectiveOffer
    venue = offer.venue
    redactor = booking.educationalRedactor

    return {
        "address": "",
        "accessibility": _get_educational_offer_accessibility(offer),
        "startDatetime": format_into_utc_date(stock.startDatetime),
        "endDatetime": format_into_utc_date(stock.endDatetime),
        "cancellationDate": format_into_utc_date(booking.cancellationDate) if booking.cancellationDate else None,
        "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
        "confirmationDate": format_into_utc_date(booking.confirmationDate) if booking.confirmationDate else None,
        "confirmationLimitDate": format_into_utc_date(booking.confirmationLimitDate),
        "contact": {"email": offer.contactEmail, "phone": offer.contactPhone},
        "creationDate": format_into_utc_date(booking.dateCreated),
        "description": offer.description,
        "durationMinutes": offer.durationMinutes,
        "expirationDate": None,
        "id": booking.id,
        "hasUrl": False,
        "venueName": venue.name,
        "name": offer.name,
        "numberOfTickets": stock.numberOfTickets,
        "participants": [students.value for students in offer.students],
        "priceDetail": stock.priceDetail,
        "price": float(stock.price),
        "quantity": 1,
        "redactor": {
            "email": redactor.email,
            "redactorFirstName": redactor.firstName,
            "redactorLastName": redactor.lastName,
            "redactorCivility": redactor.civility,
        },
        "UAICode": booking.educationalInstitution.institutionId,
        "yearId": int(booking.educationalYearId),
        "status": booking.status.value,
        "cancellationReason": booking.cancellationReason.value if booking.cancellationReason else None,
        "venueTimezone": venue.offererAddress.address.timezone,
        "totalAmount": float(stock.price),
        "url": offer_app_link(offer),
        "withdrawalDetails": None,
        "domainIds": [domain.id for domain in offer.domains],
        "domainLabels": [domain.name for domain in offer.domains],
        "interventionArea": offer.interventionArea,
        "imageUrl": offer.imageUrl,
        "imageCredit": offer.imageCredit,
        "venueId": venue.id,
        "offererName": venue.managingOfferer.name,
        "formats": sorted([format.value for format in offer.formats]),
    }
