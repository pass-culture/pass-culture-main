import dataclasses
import datetime
import decimal
import typing

from pydantic.v1 import PositiveInt
from pydantic.v1.fields import Field

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class AdageBaseResponseModel(BaseModel):
    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


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


class MergeInstitutionPrebookingsQueryModel(AdageBaseResponseModel):
    source_uai: str
    destination_uai: str
    bookings_ids: list[int]


class GetEducationalBookingsRequest(BaseModel):
    redactorEmail: str | None = Field(description="Email of querying redactor")

    class Config:
        title = "Prebookings query filters"


class EducationalBookingsResponse(AdageBaseResponseModel):
    prebookings: list[EducationalBookingResponse]

    class Config:
        title = "List of prebookings"


class EducationalBookingPerYearResponse(AdageBaseResponseModel):
    id: int
    UAICode: str
    status: models.EducationalBookingStatus | models.CollectiveBookingStatus
    cancellationReason: models.CollectiveBookingCancellationReasons | None
    confirmationLimitDate: datetime.datetime
    totalAmount: decimal.Decimal
    startDatetime: datetime.datetime
    endDatetime: datetime.datetime
    venueTimezone: str
    name: str
    redactorEmail: str
    domainIds: list[int]
    domainLabels: list[str]
    venueId: int | None
    venueName: str | None
    offererName: str | None
    formats: typing.Sequence[EacFormat]

    class Config:
        use_enum_values = True


class EducationalBookingsPerYearResponse(AdageBaseResponseModel):
    bookings: list[EducationalBookingPerYearResponse]


class GetAllBookingsPerYearQueryModel(BaseModel):
    page: PositiveInt | None
    per_page: PositiveInt | None


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class CollectiveOffersFilter:
    user_id: int
    user_is_admin: bool
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
