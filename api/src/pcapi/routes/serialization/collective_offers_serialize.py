from datetime import datetime
import enum
from typing import Optional
from typing import Union

from pydantic import Field
from pydantic import validator

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers.models import Venue
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.offers_serialize import ListOffersVenueResponseModel
from pcapi.serialization.utils import dehumanize_field
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


class ListCollectiveOffersQueryModel(BaseModel):
    nameOrIsbn: Optional[str]
    offerer_id: Optional[int]
    status: Optional[str]
    venue_id: Optional[int]
    categoryId: Optional[str]
    creation_mode: Optional[str]
    period_beginning_date: Optional[str]
    period_ending_date: Optional[str]

    _dehumanize_venue_id = dehumanize_field("venue_id")
    _dehumanize_offerer_id = dehumanize_field("offerer_id")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        arbitrary_types_allowed = True


class CollectiveOffersStockResponseModel(BaseModel):
    id: str
    hasBookingLimitDatetimePassed: bool
    offerId: str
    remainingQuantity: Union[int, str]
    beginningDatetime: Optional[datetime]

    @validator("remainingQuantity", pre=True)
    def validate_remaining_quantity(cls, remainingQuantity):  # pylint: disable=no-self-argument
        if remainingQuantity and remainingQuantity != "0" and not isinstance(remainingQuantity, int):
            return remainingQuantity.lstrip("0")
        return remainingQuantity


class CollectiveOfferResponseModel(BaseModel):
    hasBookingLimitDatetimesPassed: bool
    id: str
    isActive: bool
    isEditable: bool
    isEvent: bool
    isThing: bool
    isEducational: bool
    name: str
    stocks: list[CollectiveOffersStockResponseModel]
    thumbUrl: Optional[str]
    productIsbn: Optional[str]
    subcategoryId: SubcategoryIdEnum
    venue: ListOffersVenueResponseModel
    status: str
    venueId: str
    isShowcase: Optional[bool]


class ListCollectiveOffersResponseModel(BaseModel):
    __root__: list[CollectiveOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


def serialize_collective_offers_capped(
    paginated_offers: list[Union[CollectiveOffer, CollectiveOfferTemplate]]
) -> list[dict]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers]


def _serialize_offer_paginated(offer: Union[CollectiveOffer, CollectiveOfferTemplate]) -> dict:
    # TODO: put back offer.id when we will use new api routes on frontend side
    serialized_stock = [_serialize_stock(offer.offerId, getattr(offer, "collectiveStock", None))]
    is_offer_template = isinstance(offer, CollectiveOfferTemplate)

    return {
        "hasBookingLimitDatetimesPassed": offer.hasBookingLimitDatetimesPassed if not is_offer_template else False,
        # TODO: put back offer.id when we will use new api routes on frontend side
        "id": humanize(offer.offerId),
        "isActive": offer.isActive,
        "isEditable": True,
        "isEvent": True,
        "isThing": False,
        "isEducational": True,
        "productIsbn": None,
        "name": offer.name,
        "stocks": serialized_stock,
        "thumbUrl": None,
        "subcategoryId": offer.subcategoryId,
        "venue": _serialize_venue(offer.venue),
        "venueId": humanize(offer.venue.id),
        "status": offer.status.name,
        "isShowcase": is_offer_template,
    }


def _serialize_stock(offer_id: int, stock: Optional[CollectiveStock] = None) -> dict:
    if stock:
        # TODO: put back stock.id when we will use new api routes on frontend side
        return {
            "id": humanize(stock.stockId),
            "offerId": humanize(offer_id),
            "hasBookingLimitDatetimePassed": stock.hasBookingLimitDatetimePassed,
            "remainingQuantity": 1,
            "beginningDatetime": stock.beginningDatetime,
        }
    return {
        "id": humanize(0),
        "offerId": humanize(offer_id),
        "hasBookingLimitDatetimePassed": False,
        "remainingQuantity": 1,
        "beginningDatetime": datetime(year=2030, month=1, day=1),
    }


def _serialize_venue(venue: Venue) -> dict:
    return {
        "id": humanize(venue.id),
        "isVirtual": venue.isVirtual,
        "managingOffererId": humanize(venue.managingOffererId),
        "name": venue.name,
        "offererName": venue.managingOfferer.name,
        "publicName": venue.publicName,
        "departementCode": venue.departementCode,
    }


class GetCollectiveOfferManagingOffererResponseModel(BaseModel):
    address: Optional[str]
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: Optional[datetime]
    id: str
    idAtProviders: Optional[str]
    isActive: bool
    isValidated: bool
    lastProviderId: Optional[str]
    name: str
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: Optional[str]
    thumbCount: int

    _humanize_id = humanize_field("id")
    _humanize_last_provider_id = humanize_field("lastProviderId")

    class Config:
        orm_mode = True


class GetCollectiveOfferVenueResponseModel(BaseModel):
    address: Optional[str]
    bookingEmail: Optional[str]
    city: Optional[str]
    comment: Optional[str]
    dateCreated: Optional[datetime]
    dateModifiedAtLastProvider: Optional[datetime]
    departementCode: Optional[str]
    fieldsUpdated: list[str]
    id: str
    idAtProviders: Optional[str]
    isValidated: bool
    isVirtual: bool
    lastProviderId: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    managingOfferer: GetCollectiveOfferManagingOffererResponseModel
    managingOffererId: str
    name: str
    postalCode: Optional[str]
    publicName: Optional[str]
    siret: Optional[str]
    thumbCount: int
    venueLabelId: Optional[str]
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]

    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_last_provider_id = humanize_field("lastProviderId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class OfferAddressType(enum.Enum):
    OFFERER_VENUE = "offererVenue"
    SCHOOL = "school"
    OTHER = "other"


class CollectiveOfferOfferVenueResponseModel(BaseModel):
    addressType: OfferAddressType
    otherAddress: str
    venueId: str


class GetCollectiveOfferCollectiveStockResponseModel(BaseModel):
    id: str
    isSoldOut: bool = Field(alias="isBooked")

    _humanize_id = humanize_field("id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}


class GetCollectiveOfferResponseModel(BaseModel):
    bookingEmail: Optional[str]
    dateCreated: datetime
    description: Optional[str]
    durationMinutes: Optional[int]
    students: list[StudentLevels]
    offerVenue: CollectiveOfferOfferVenueResponseModel
    contactEmail: str
    contactPhone: str
    hasBookingLimitDatetimesPassed: bool
    id: str
    isActive: bool
    isBookable: bool
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    nonHumanizedId: int
    visualDisabilityCompliant: Optional[bool]
    name: str
    stock: GetCollectiveOfferCollectiveStockResponseModel = Field(alias="collectiveStock")
    subcategoryId: SubcategoryIdEnum
    venue: GetCollectiveOfferVenueResponseModel
    venueId: str
    status: OfferStatus

    _humanize_id = humanize_field("id")
    _humanize_venue_id = humanize_field("venueId")

    @classmethod
    def from_orm(cls, offer):  # type: ignore
        offer.nonHumanizedId = offer.id
        return super().from_orm(offer)

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True
