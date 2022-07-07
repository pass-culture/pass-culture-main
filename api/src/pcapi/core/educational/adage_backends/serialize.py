from datetime import datetime

from pcapi.core.educational import models
from pcapi.routes.adage.v1.serialization.config import AdageBaseResponseModel
from pcapi.routes.native.v1.serialization.common_models import Coordinates


class CollectiveOfferNotAssociatedToInstitution(Exception):
    pass


class AdageCollectiveOfferContact(AdageBaseResponseModel):
    email: str
    phone: str


class AdageCollectiveOffer(AdageBaseResponseModel):
    UAICode: str
    address: str
    beginningDatetime: datetime
    city: str
    contact: AdageCollectiveOfferContact
    coordinates: Coordinates
    description: str | None
    durationMinutes: float | None
    id: int
    name: str
    numberOfTickets: int
    participants: list[models.StudentLevels]
    postalCode: str
    price: float
    priceDetail: str | None
    quantity: int
    subcategoryLabel: str
    totalAmount: float
    venueName: str
    venueTimezone: str
    isDigital: bool
    withdrawalDetails: str | None


def _get_collective_offer_address(offer: models.CollectiveOffer) -> str:
    default_address = f"{offer.venue.address}, {offer.venue.postalCode} {offer.venue.city}"

    if offer.offerVenue is None:
        return default_address

    address_type = offer.offerVenue["addressType"]

    if address_type == "offererVenue":
        return default_address

    if address_type == "other":
        return offer.offerVenue["otherAddress"]  # type: ignore[return-value]

    if address_type == "school":
        return "Dans l’établissement scolaire"

    return default_address


def serialize_collective_offer(collective_offer: models.CollectiveOffer) -> AdageCollectiveOffer:
    stock = collective_offer.collectiveStock
    venue = collective_offer.venue
    institution = collective_offer.institution

    if not institution:
        raise CollectiveOfferNotAssociatedToInstitution()

    return AdageCollectiveOffer(
        UAICode=institution.institutionId,
        address=_get_collective_offer_address(collective_offer),
        beginningDatetime=stock.beginningDatetime,
        city=venue.city,
        contact=AdageCollectiveOfferContact(phone=collective_offer.contactPhone, email=collective_offer.contactEmail),
        coordinates=Coordinates(latitude=venue.latitude, longitude=venue.longitude),
        description=collective_offer.description,
        durationMinutes=collective_offer.durationMinutes,
        id=collective_offer.id,
        name=collective_offer.name,
        numberOfTickets=stock.numberOfTickets,
        participants=collective_offer.students,
        postalCode=venue.postalCode,
        price=stock.price,
        priceDetail=stock.priceDetail,
        quantity=1,
        subcategoryLabel=collective_offer.subcategory.app_label,
        totalAmount=stock.price,
        venueName=venue.name,
        venueTimezone=venue.timezone,
        isDigital=False,
        withdrawalDetails=None,
    )
