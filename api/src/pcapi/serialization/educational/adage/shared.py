import datetime
import decimal

from pydantic.v1.fields import Field

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.models import feature
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class AdageBaseResponseModel(BaseModel):
    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class AdageCollectiveOfferContact(AdageBaseResponseModel):
    email: str | None
    phone: str | None


class AdageRedactor(AdageBaseResponseModel):
    email: str | None
    redactorCivility: str | None
    redactorFirstName: str | None
    redactorLastName: str | None


class AdageCollectiveOffer(AdageBaseResponseModel):
    UAICode: str
    address: str
    startDatetime: datetime.datetime
    endDatetime: datetime.datetime
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
    isDigital: bool
    withdrawalDetails: str | None
    redactor: AdageRedactor | None


def _get_collective_offer_address_with_oa(offer: models.CollectiveOffer) -> str:
    match offer.locationType:
        case models.CollectiveLocationType.SCHOOL:
            return "Dans l'établissement scolaire"

        case models.CollectiveLocationType.ADDRESS:
            if offer.offererAddress is None:
                return ""

            return offer.offererAddress.address.fullAddress

        case models.CollectiveLocationType.TO_BE_DEFINED:
            return offer.locationComment or ""

        case _:
            return ""


def get_collective_offer_address(offer: models.CollectiveOffer) -> str:
    if feature.FeatureToggle.WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE.is_active():
        return _get_collective_offer_address_with_oa(offer)

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


def serialize_collective_offer(collective_offer: models.CollectiveOffer) -> AdageCollectiveOffer:
    stock = collective_offer.collectiveStock
    venue = collective_offer.venue
    institution = collective_offer.institution

    if not institution:
        raise exceptions.CollectiveOfferNotAssociatedToInstitution()

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


class AdageEducationalInstitution(AdageBaseResponseModel):
    uai: str
    sigle: str
    libelle: str
    communeLibelle: str
    courriel: str | None
    telephone: str | None
    codePostal: str
    latitude: decimal.Decimal | None
    longitude: decimal.Decimal | None


class AdageCollectiveRequest(AdageBaseResponseModel):
    redactorEmail: str
    requestPhoneNumber: str | None
    requestedDate: datetime.date | None
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


class AdageCulturalPartner(BaseModel):
    id: int
    venueId: int | None
    siret: str | None
    regionId: int | None
    academieId: str | None
    statutId: int | None
    labelId: int | None
    typeId: int | None
    communeId: str | None
    libelle: str
    adresse: str | None
    siteWeb: str | None
    latitude: float | None
    longitude: float | None
    statutLibelle: str | None
    labelLibelle: str | None
    typeIcone: str | None
    typeLibelle: str | None
    communeLibelle: str | None
    communeDepartement: str | None
    academieLibelle: str | None
    regionLibelle: str | None
    domaines: str | None
    actif: int | None
    dateModification: datetime.datetime
    synchroPass: int | None
    domaineIds: str | None


class AdageCulturalPartners(BaseModel):
    partners: list[AdageCulturalPartner]


class Contact(AdageBaseResponseModel):
    email: str | None
    phone: str | None


class Redactor(AdageBaseResponseModel):
    email: str
    redactorFirstName: str | None
    redactorLastName: str | None
    redactorCivility: str | None

    class Config:
        alias_generator = to_camel


class EducationalBookingResponse(AdageBaseResponseModel):
    accessibility: str = Field(description="Accessibility of the offer")
    address: str = Field(description="Adresse of event")
    startDatetime: datetime.datetime = Field(description="Start date of event")
    endDatetime: datetime.datetime = Field(description="End date of event")
    cancellationDate: datetime.datetime | None = Field(description="Date of cancellation if prebooking is cancelled")
    cancellationLimitDate: datetime.datetime | None = Field(description="Limit date to cancel the prebooking")
    confirmationDate: datetime.datetime | None = Field(description="Date of confirmation if prebooking is confirmed")
    confirmationLimitDate: datetime.datetime = Field(description="Limit date to confirm the prebooking")
    contact: Contact = Field(description="Contact of the prebooking")
    creationDate: datetime.datetime
    description: str | None = Field(description="Offer description")
    durationMinutes: int | None = Field(description="Offer's duration in minutes")
    expirationDate: datetime.datetime | None = Field(description="Expiration date after which booking is cancelled")
    id: int = Field(description="pass Culture's prebooking id")
    isDigital: bool = Field(description="If true the event is accessed digitally")
    venueName: str = Field(description="Name of cultural venue proposing the event")
    name: str = Field(description="Name of event")
    numberOfTickets: int | None = Field(description="Number of tickets")
    price: decimal.Decimal
    quantity: int = Field(description="Number of place prebooked")
    redactor: Redactor
    UAICode: str = Field(description="Educational institution UAI code")
    yearId: int = Field(description="Shared year id")
    status: models.EducationalBookingStatus | models.CollectiveBookingStatus
    cancellationReason: models.CollectiveBookingCancellationReasons | None = Field(
        description="Reason when a prebooking order is cancelled"
    )
    participants: list[str] = Field(description="List of class levels which can participate")
    priceDetail: str | None = Field(description="Offer's stock price detail")
    venueTimezone: str
    totalAmount: decimal.Decimal = Field(description="Total price of the prebooking")
    url: str | None = Field(description="Url to access the offer")
    withdrawalDetails: str | None
    domain_ids: list[int]
    domain_labels: list[str]
    interventionArea: list[str]
    imageCredit: str | None = Field(description="Credit for the source image")
    imageUrl: str | None = Field(description="Url for offer image")
    venueId: int
    offererName: str
    formats: list[EacFormat]

    class Config:
        title = "Prebooking detailed response"
        alias_generator = to_camel
        allow_population_by_field_name = True


class EducationalBookingEdition(EducationalBookingResponse):
    updatedFields: list[str] = Field(description="List of fields updated")


class AdageReimbursementNotification(EducationalBookingResponse):
    reimbursementReason: str
    reimbursedValue: decimal.Decimal
    reimbursementDetails: str


class RedactorInformation(BaseModel):
    civility: str | None
    lastname: str | None
    firstname: str | None
    email: str
    uai: str
