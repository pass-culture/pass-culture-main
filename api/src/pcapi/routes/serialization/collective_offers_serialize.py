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
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


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
    def validate_remaining_quantity(cls, remainingQuantity):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
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
    offerId: Optional[str]


class ListCollectiveOffersResponseModel(BaseModel):
    __root__: list[CollectiveOfferResponseModel]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


def serialize_collective_offers_capped(
    paginated_offers: list[Union[CollectiveOffer, CollectiveOfferTemplate]]
) -> list[CollectiveOfferResponseModel]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers]


def _serialize_offer_paginated(offer: Union[CollectiveOffer, CollectiveOfferTemplate]) -> CollectiveOfferResponseModel:
    # TODO: put back offer.id when we will use new api routes on frontend side
    serialized_stock = [_serialize_stock(offer.offerId, getattr(offer, "collectiveStock", None))]  # type: ignore [arg-type]
    is_offer_template = isinstance(offer, CollectiveOfferTemplate)

    return CollectiveOfferResponseModel(
        hasBookingLimitDatetimesPassed=offer.hasBookingLimitDatetimesPassed if not is_offer_template else False,
        id=humanize(offer.id),
        isActive=offer.isActive,
        isEditable=True,
        isEvent=True,
        isThing=False,
        isEducational=True,
        productIsbn=None,
        name=offer.name,
        stocks=serialized_stock,
        thumbUrl=None,
        subcategoryId=offer.subcategoryId,
        venue=_serialize_venue(offer.venue),
        venueId=humanize(offer.venue.id),
        status=offer.status.name,  # type: ignore [attr-defined]
        isShowcase=is_offer_template,
        offerId=humanize(offer.offerId),
    )


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


class GetCollectiveOfferBaseResponseModel(BaseModel):
    id: str
    bookingEmail: Optional[str]
    dateCreated: datetime
    description: Optional[str]
    durationMinutes: Optional[int]
    students: list[StudentLevels]
    offerVenue: CollectiveOfferOfferVenueResponseModel
    contactEmail: str
    contactPhone: str
    hasBookingLimitDatetimesPassed: bool
    offerId: Optional[str]
    isActive: bool
    audioDisabilityCompliant: Optional[bool]
    mentalDisabilityCompliant: Optional[bool]
    motorDisabilityCompliant: Optional[bool]
    visualDisabilityCompliant: Optional[bool]
    nonHumanizedId: int
    name: str
    subcategoryId: SubcategoryIdEnum
    venue: GetCollectiveOfferVenueResponseModel
    venueId: str
    status: OfferStatus

    _humanize_id = humanize_field("id")
    _humanize_offerId = humanize_field("offerId")
    _humanize_venue_id = humanize_field("venueId")

    @classmethod
    def from_orm(cls, offer):  # type: ignore
        offer.nonHumanizedId = offer.id
        return super().from_orm(offer)

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class GetCollectiveOfferTemplateResponseModel(GetCollectiveOfferBaseResponseModel):
    priceDetail: Optional[str]


class GetCollectiveOfferResponseModel(GetCollectiveOfferBaseResponseModel):
    isBookable: bool
    stock: GetCollectiveOfferCollectiveStockResponseModel = Field(alias="collectiveStock")


class CollectiveOfferResponseIdModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class CollectiveOfferExtraDataOfferVenueBodyModel(BaseModel):
    addressType: OfferAddressType
    otherAddress: str
    venueId: str

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PostCollectiveOfferBodyModel(BaseModel):
    offerer_id: str
    venue_id: str
    subcategory_id: str
    name: str
    booking_email: Optional[str]
    description: Optional[str]
    duration_minutes: Optional[int]
    audio_disability_compliant: bool = False
    mental_disability_compliant: bool = False
    motor_disability_compliant: bool = False
    visual_disability_compliant: bool = False
    students: list[StudentLevels]
    offer_venue: CollectiveOfferExtraDataOfferVenueBodyModel
    contact_email: str
    contact_phone: str

    @validator("name", pre=True)
    def validate_name(cls: BaseModel, name: str, values: str) -> str:  # pylint: disable=no-self-argument
        check_offer_name_length_is_valid(name)
        return name

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOfferTemplateBodyModel(BaseModel):
    price_detail: Optional[str] = Field(alias="educationalPriceDetail")

    @validator("price_detail")
    def validate_price_detail(cls, price_detail: Optional[str]) -> Optional[str]:  # pylint: disable=no-self-argument
        if price_detail and len(price_detail) > 1000:
            raise ValueError("Le détail du prix ne doit pas excéder 1000 caractères.")
        return price_detail

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class CollectiveOfferTemplateResponseIdModel(BaseModel):
    id: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
