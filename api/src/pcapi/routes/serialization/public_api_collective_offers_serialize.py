from pcapi.core.educational.models import CollectiveOffer
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class ListCollectiveOffersQueryModel(BaseModel):
    status: OfferStatus | None
    venue_id: int | None
    period_beginning_date: str | None
    period_ending_date: str | None

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOffersResponseModel(BaseModel):
    id: int
    beginningDatetime: str
    status: str
    venueId: int

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "CollectiveOffersResponseModel":
        return cls(
            id=offer.id,
            beginningDatetime=offer.collectiveStock.beginningDatetime.replace(microsecond=0).isoformat(),
            status=offer.status.name,  # type: ignore [attr-defined]
            venueId=offer.venueId,
        )


class CollectiveOffersListResponseModel(BaseModel):
    __root__: list[CollectiveOffersResponseModel]


class CollectiveOffersVenueResponseModel(BaseModel):
    id: int
    name: str
    address: str | None
    postalCode: str | None
    city: str | None

    class Config:
        orm_mode = True


class CollectiveOffersListVenuesResponseModel(BaseModel):
    __root__: list[CollectiveOffersVenueResponseModel]


class CollectiveOffersCategoryResponseModel(BaseModel):
    id: str
    name: str


class CollectiveOffersListCategoriesResponseModel(BaseModel):
    __root__: list[CollectiveOffersCategoryResponseModel]


class CollectiveOffersDomainResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CollectiveOffersListDomainsResponseModel(BaseModel):
    __root__: list[CollectiveOffersDomainResponseModel]


class CollectiveOffersStudentLevelResponseModel(BaseModel):
    id: str
    name: str


class CollectiveOffersListStudentLevelsResponseModel(BaseModel):
    __root__: list[CollectiveOffersStudentLevelResponseModel]


class GetPublicCollectiveOfferResponseModel(BaseModel):
    id: int
    status: str
    name: str
    description: str | None
    subcategoryId: str
    bookingEmail: str | None
    contactEmail: str
    contactPhone: str
    domains: list[str]
    durationMinutes: int | None
    interventionArea: list[str]
    students: list[str]
    dateCreated: str
    hasBookingLimitDatetimesPassed: bool
    isActive: bool | None
    isSoldOut: bool
    venueId: int
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None
    address: str
    beginningDatetime: str
    bookingLimitDatetime: str
    totalPrice: int
    numberOfTickets: int
    educationalPriceDetail: str | None
    educationalInstitution: str | None

    class Config:
        extra = "forbid"
        orm_mode = True

    @classmethod
    def from_orm(cls, offer: CollectiveOffer) -> "GetPublicCollectiveOfferResponseModel":
        return cls(
            id=offer.id,
            status=offer.status.name,  # type: ignore [attr-defined]
            name=offer.name,
            description=offer.description,
            subcategoryId=offer.subcategoryId,
            bookingEmail=offer.bookingEmail,
            contactEmail=offer.contactEmail,
            contactPhone=offer.contactPhone,
            domains=[domain.name for domain in offer.domains],
            durationMinutes=offer.durationMinutes,
            interventionArea=offer.interventionArea,
            students=[student.name for student in offer.students],
            dateCreated=offer.dateCreated.replace(microsecond=0).isoformat(),  # type: ignore [union-attr]
            hasBookingLimitDatetimesPassed=offer.hasBookingLimitDatetimesPassed,
            isActive=offer.isActive,
            isSoldOut=offer.isSoldOut,
            venueId=offer.venueId,
            audioDisabilityCompliant=offer.audioDisabilityCompliant,
            mentalDisabilityCompliant=offer.mentalDisabilityCompliant,
            motorDisabilityCompliant=offer.motorDisabilityCompliant,
            visualDisabilityCompliant=offer.visualDisabilityCompliant,
            address=offer.venue.address,
            beginningDatetime=offer.collectiveStock.beginningDatetime.replace(microsecond=0).isoformat(),
            bookingLimitDatetime=offer.collectiveStock.bookingLimitDatetime.replace(microsecond=0).isoformat(),
            totalPrice=(offer.collectiveStock.price * 100),
            numberOfTickets=offer.collectiveStock.numberOfTickets,
            educationalPriceDetail=offer.collectiveStock.priceDetail,
            educationalInstitution=offer.institution.institutionId if offer.institutionId else None,
        )
