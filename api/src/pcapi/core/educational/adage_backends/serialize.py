import decimal
from datetime import date
from datetime import datetime

from pcapi.core.educational import models
from pcapi.core.educational import schemas


class CollectiveOfferNotAssociatedToInstitution(Exception):
    pass


class AdageCollectiveOfferContact(schemas.AdageBaseResponseModel):
    email: str | None
    phone: str | None


class AdageRedactor(schemas.AdageBaseResponseModel):
    email: str | None
    redactorCivility: str | None
    redactorFirstName: str | None
    redactorLastName: str | None


class AdageCollectiveOffer(schemas.AdageBaseResponseModel):
    UAICode: str
    address: str
    startDatetime: datetime
    endDatetime: datetime
    contact: AdageCollectiveOfferContact
    description: str | None
    durationMinutes: float | None
    id: int
    name: str
    numberOfTickets: int
    participants: list[models.StudentLevels]
    price: decimal.Decimal
    priceDetail: str | None
    quantity: int
    totalAmount: decimal.Decimal
    venueName: str
    venueTimezone: str
    hasUrl: bool
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
        address=get_collective_offer_address(collective_offer),
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        contact=AdageCollectiveOfferContact(phone=collective_offer.contactPhone, email=collective_offer.contactEmail),
        description=collective_offer.description,
        durationMinutes=collective_offer.durationMinutes,
        id=collective_offer.id,
        name=collective_offer.name,
        numberOfTickets=stock.numberOfTickets,
        participants=collective_offer.students,
        price=stock.price,
        priceDetail=stock.priceDetail,
        quantity=1,
        totalAmount=stock.price,
        venueName=venue.name,
        venueTimezone=venue.offererAddress.address.timezone,
        hasUrl=False,
        withdrawalDetails=None,
        redactor=AdageRedactor(
            email=collective_offer.teacher.email if collective_offer.teacher else None,
            redactorCivility=collective_offer.teacher.civility if collective_offer.teacher else None,
            redactorFirstName=collective_offer.teacher.firstName if collective_offer.teacher else None,
            redactorLastName=collective_offer.teacher.lastName if collective_offer.teacher else None,
        )
        or None,
    )


def get_collective_offer_address(offer: models.CollectiveOffer) -> str:
    match offer.locationType:
        case models.CollectiveLocationType.SCHOOL:
            return "Dans l'établissement scolaire"

        case models.CollectiveLocationType.ADDRESS:
            if offer.offererAddress is None:
                return ""

            return offer.offererAddress.address.fullAddress

        case models.CollectiveLocationType.TO_BE_DEFINED:
            return offer.locationComment or ""


class AdageEducationalInstitution(schemas.AdageBaseResponseModel):
    uai: str
    sigle: str
    libelle: str
    communeLibelle: str
    courriel: str | None
    telephone: str | None
    codePostal: str
    latitude: decimal.Decimal | None
    longitude: decimal.Decimal | None


class AdageCollectiveRequest(schemas.AdageBaseResponseModel):
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
