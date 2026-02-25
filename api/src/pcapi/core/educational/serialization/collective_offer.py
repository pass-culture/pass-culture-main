from pcapi.core.educational import models
from pcapi.core.educational import schemas


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


class CollectiveOfferNotAssociatedToInstitution(Exception):
    pass


def serialize_collective_offer(collective_offer: models.CollectiveOffer) -> schemas.AdageCollectiveOffer:
    stock = collective_offer.collectiveStock
    venue = collective_offer.venue
    institution = collective_offer.institution

    if not institution:
        raise CollectiveOfferNotAssociatedToInstitution()

    return schemas.AdageCollectiveOffer(
        UAICode=institution.institutionId,
        address=get_collective_offer_address(collective_offer),
        startDatetime=stock.startDatetime,
        endDatetime=stock.endDatetime,
        contact=schemas.AdageCollectiveOfferContact(
            phone=collective_offer.contactPhone, email=collective_offer.contactEmail
        ),
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
        redactor=schemas.AdageRedactor(
            email=collective_offer.teacher.email if collective_offer.teacher else None,
            redactorCivility=collective_offer.teacher.civility if collective_offer.teacher else None,
            redactorFirstName=collective_offer.teacher.firstName if collective_offer.teacher else None,
            redactorLastName=collective_offer.teacher.lastName if collective_offer.teacher else None,
        )
        or None,
    )
