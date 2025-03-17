from datetime import date
from datetime import datetime
import decimal

from pcapi.core.educational import models
import pcapi.core.educational.schemas as educational_schemas


class CollectiveOfferNotAssociatedToInstitution(Exception):
    pass


class AdageCollectiveOfferContact(educational_schemas.AdageBaseResponseModel):
    email: str | None
    phone: str | None


class AdageRedactor(educational_schemas.AdageBaseResponseModel):
    email: str | None
    redactorCivility: str | None
    redactorFirstName: str | None
    redactorLastName: str | None


class AdageCollectiveOffer(educational_schemas.AdageBaseResponseModel):
    UAICode: str
    address: str
    startDatetime: datetime
    endDatetime: datetime
    city: str
    contact: AdageCollectiveOfferContact
    coordinates: educational_schemas.Coordinates
    description: str | None
    durationMinutes: float | None
    id: int
    name: str
    numberOfTickets: int
    participants: list[models.StudentLevels]
    postalCode: str
    price: decimal.Decimal
    priceDetail: str | None
    quantity: int
    subcategoryLabel: str
    totalAmount: decimal.Decimal
    venueName: str
    venueTimezone: str
    isDigital: bool
    withdrawalDetails: str | None
    redactor: AdageRedactor | None


def serialize_collective_offer(collective_offer: models.CollectiveOffer) -> AdageCollectiveOffer:
    stock = collective_offer.collectiveStock
    venue = collective_offer.venue
    institution = collective_offer.institution

    if not institution:
        raise CollectiveOfferNotAssociatedToInstitution()

    return AdageCollectiveOffer(
        UAICode=institution.institutionId,
        address=_get_collective_offer_address(collective_offer),
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        city=venue.city,  # type: ignore[arg-type]  # TODO: check that it cannot be None
        contact=AdageCollectiveOfferContact(phone=collective_offer.contactPhone, email=collective_offer.contactEmail),
        coordinates=educational_schemas.Coordinates(latitude=venue.latitude, longitude=venue.longitude),
        description=collective_offer.description,
        durationMinutes=collective_offer.durationMinutes,
        id=collective_offer.id,
        name=collective_offer.name,
        numberOfTickets=stock.numberOfTickets,
        participants=collective_offer.students,
        postalCode=venue.postalCode,  # type: ignore[arg-type]  # TODO: check that it cannot be None
        price=stock.price,
        priceDetail=stock.priceDetail,
        quantity=1,
        subcategoryLabel=collective_offer.subcategory.app_label if collective_offer.subcategory else "",
        totalAmount=stock.price,
        venueName=venue.name,
        venueTimezone=venue.timezone,
        isDigital=False,
        withdrawalDetails=None,
        redactor=AdageRedactor(
            email=collective_offer.teacher.email if collective_offer.teacher else None,
            redactorCivility=collective_offer.teacher.civility if collective_offer.teacher else None,
            redactorFirstName=collective_offer.teacher.firstName if collective_offer.teacher else None,
            redactorLastName=collective_offer.teacher.lastName if collective_offer.teacher else None,
        )
        or None,
    )


def _get_collective_offer_address(offer: models.CollectiveOffer) -> str:
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


class AdageEducationalInstitution(educational_schemas.AdageBaseResponseModel):
    uai: str
    sigle: str
    libelle: str
    communeLibelle: str
    courriel: str | None
    telephone: str | None
    codePostal: str
    latitude: decimal.Decimal | None
    longitude: decimal.Decimal | None


class AdageCollectiveRequest(educational_schemas.AdageBaseResponseModel):
    redactorEmail: str
    requestPhoneNumber: str | None
    requestedDate: date | None
    totalStudents: int | None
    totalTeachers: int | None
    offerContactEmail: str | None
    offerContactPhoneNumber: str | None
    offererName: str
    venueName: str
    offerName: str
    comment: str


def serialize_collective_offer_request(request: models.CollectiveOfferRequest) -> AdageCollectiveRequest:
    return AdageCollectiveRequest(
        redactorEmail=request.educationalRedactor.email,
        requestPhoneNumber=request._phoneNumber,
        requestedDate=request.requestedDate,
        totalStudents=request.totalStudents,
        totalTeachers=request.totalTeachers,
        comment=request.comment,
        offerContactEmail=request.collectiveOfferTemplate.contactEmail,
        offerContactPhoneNumber=request.collectiveOfferTemplate.contactPhone,
        offererName=request.collectiveOfferTemplate.venue.managingOfferer.name,
        venueName=request.collectiveOfferTemplate.venue.name,
        offerName=request.collectiveOfferTemplate.name,
    )
