import dataclasses
import datetime
import decimal
import typing

import pydantic as pydantic_v2
from pydantic.v1.fields import Field

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models
from pcapi.core.educational.utils import format_collective_additional_fee_type
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class AdageBaseResponseModel(BaseModel):
    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class AdageCulturalPartner(pydantic_v2.BaseModel):
    id: int
    venueId: int | None = None
    siret: str | None = None
    regionId: int | None = None
    academieId: str | None = None
    statutId: int | None = None
    labelId: int | None = None
    typeId: int | None = None
    communeId: str | None = None
    libelle: str
    adresse: str | None = None
    siteWeb: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    statutLibelle: str | None = None
    labelLibelle: str | None = None
    typeIcone: str | None = None
    typeLibelle: str | None = None
    communeLibelle: str | None = None
    communeDepartement: str | None = None
    academieLibelle: str | None = None
    regionLibelle: str | None = None
    domaines: str | None = None
    actif: int | None = None
    dateModification: datetime.datetime
    synchroPass: int | None = None
    domaineIds: str | None = None


class AdageContact(pydantic_v2.BaseModel):
    email: str | None
    phone: str | None


class AdageRedactor(pydantic_v2.BaseModel):
    email: str | None
    redactorCivility: str | None
    redactorFirstName: str | None
    redactorLastName: str | None


class Contact(AdageBaseResponseModel):
    email: str | None
    phone: str | None


class Redactor(AdageBaseResponseModel):
    email: str
    redactorFirstName: str | None
    redactorLastName: str | None
    redactorCivility: str | None


CollectiveBookingRefused = typing.Literal["REFUSED"]


class AdditionalFeeResponse(AdageBaseResponseModel):
    label: str
    amount: decimal.Decimal

    @classmethod
    def build(cls, fee: models.CollectiveAdditionalFee) -> typing.Self:
        label = fee.label if fee.label else format_collective_additional_fee_type(fee.type)

        return cls(label=label, amount=fee.amount)


class AdditionalFeeResponseV2(HttpBodyModel):
    label: str
    amount: float

    @classmethod
    def build(cls, fee: models.CollectiveAdditionalFee) -> typing.Self:
        label = fee.label if fee.label else format_collective_additional_fee_type(fee.type)

        return cls(label=label, amount=float(fee.amount))


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
    additionalDetails: str | None = Field(description="Practical information on the offer")
    durationMinutes: int | None = Field(description="Offer's duration in minutes")
    id: int = Field(description="pass Culture's prebooking id")
    venueName: str = Field(description="Name of cultural venue proposing the event")
    name: str = Field(description="Name of event")
    numberOfTickets: int = Field(description="Number of students")
    numberOfTeachers: int = Field(description="Number of adults accompanying the students")
    price: decimal.Decimal = Field(description="Total price of the prebooking")
    servicePrice: decimal.Decimal = Field(description="Total price minus the additional fees")
    additionalFees: list[AdditionalFeeResponse] = Field(description="Fees related to transport, accommodation...")
    redactor: Redactor
    UAICode: str = Field(description="Educational institution UAI code")
    yearId: int = Field(description="Shared year id")
    status: models.CollectiveBookingStatus | CollectiveBookingRefused
    cancellationReason: models.CollectiveBookingCancellationReasons | None = Field(
        description="Reason when a prebooking order is cancelled"
    )
    participants: list[str] = Field(description="List of class levels which can participate")
    priceDetail: str | None = Field(description="Offer's stock price detail")
    venueTimezone: str
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


class RedactorInformation(pydantic_v2.BaseModel):
    civility: str | None
    lastname: str | None
    firstname: str | None
    email: str
    uai: str


class EducationalBookingsResponse(AdageBaseResponseModel):
    prebookings: list[EducationalBookingResponse]

    class Config:
        title = "List of prebookings"


class EducationalDepositPeriodResponse(AdageBaseResponseModel):
    start: datetime.datetime
    end: datetime.datetime


class EducationalDepositPeriodResponseV2(HttpBodyModel):
    start: datetime.datetime
    end: datetime.datetime


class AdageEducationalInstitution(pydantic_v2.BaseModel):
    uai: str
    sigle: str
    libelle: str
    communeLibelle: str
    courriel: str | None = None
    telephone: str | None = None
    codePostal: str
    latitude: decimal.Decimal | None = None
    longitude: decimal.Decimal | None = None


def get_adage_collective_offer_address(offer: models.CollectiveOffer) -> str:
    match offer.locationType:
        case models.CollectiveLocationType.SCHOOL:
            return "Dans l'établissement scolaire"

        case models.CollectiveLocationType.ADDRESS:
            if offer.offererAddress is None:
                return ""

            return offer.offererAddress.address.fullAddress

        case models.CollectiveLocationType.TO_BE_DEFINED:
            return offer.locationComment or ""


class AdageCollectiveOffer(pydantic_v2.BaseModel):
    UAICode: str
    address: str
    startDatetime: datetime.datetime
    endDatetime: datetime.datetime
    contact: AdageContact
    description: str | None
    additionalDetails: str | None
    durationMinutes: int | None
    id: int
    name: str
    numberOfTickets: int
    numberOfTeachers: int
    participants: list[models.StudentLevels]
    price: decimal.Decimal
    servicePrice: decimal.Decimal
    additionalFees: list[AdditionalFeeResponseV2]
    priceDetail: str | None
    venueName: str
    venueTimezone: str
    redactor: AdageRedactor | None

    model_config = pydantic_v2.ConfigDict(
        json_encoders={datetime.datetime: format_into_utc_date},
    )

    @classmethod
    def build(cls, collective_offer: models.CollectiveOffer) -> typing.Self:
        stock = collective_offer.collectiveStock
        venue = collective_offer.venue
        institution = collective_offer.institution

        # this model is used by notify_institution_association, which is called after an institution has been set
        assert institution is not None

        if collective_offer.teacher is None:
            redactor = AdageRedactor(email=None, redactorCivility=None, redactorFirstName=None, redactorLastName=None)
        else:
            redactor = AdageRedactor(
                email=collective_offer.teacher.email,
                redactorCivility=collective_offer.teacher.civility,
                redactorFirstName=collective_offer.teacher.firstName,
                redactorLastName=collective_offer.teacher.lastName,
            )

        return cls(
            UAICode=institution.institutionId,
            address=get_adage_collective_offer_address(collective_offer),
            startDatetime=stock.startDatetime,
            endDatetime=stock.endDatetime,
            contact=AdageContact(phone=collective_offer.contactPhone, email=collective_offer.contactEmail),
            description=collective_offer.description,
            additionalDetails=collective_offer.additionalDetails,
            durationMinutes=collective_offer.durationMinutes,
            id=collective_offer.id,
            name=collective_offer.name,
            numberOfTickets=stock.numberOfTickets,
            numberOfTeachers=stock.numberOfTeachers,
            participants=collective_offer.students,
            price=stock.price,
            servicePrice=stock.servicePrice,
            additionalFees=[AdditionalFeeResponseV2.build(fee) for fee in stock.collectiveAdditionalFees],
            priceDetail=stock.priceDetail,
            venueName=venue.name,
            venueTimezone=venue.offererAddress.address.timezone,
            redactor=redactor,
        )


class AdageCollectiveRequest(pydantic_v2.BaseModel):
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

    @classmethod
    def build(cls, request: models.CollectiveOfferRequest) -> typing.Self:
        return cls(
            redactorEmail=request.educationalRedactor.email,
            requestPhoneNumber=request.phoneNumber,
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


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class CollectiveOffersFilter:
    user_id: int
    offerer_id: int | None = None
    statuses: list[models.CollectiveOfferDisplayedStatus] | None = None
    venue_id: int | None = None
    provider_id: int | None = None
    name_keywords: str | None = None
    period_beginning_date: datetime.date | None = None
    period_ending_date: datetime.date | None = None
    formats: list[EacFormat] | None = None
    location_type: models.CollectiveLocationType | None = None
    offerer_address_id: int | None = None
