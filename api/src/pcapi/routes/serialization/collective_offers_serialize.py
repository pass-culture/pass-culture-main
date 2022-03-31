from datetime import datetime
from typing import Optional
from typing import Union

from pydantic import validator

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offerers.models import Venue
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.offers_serialize import ListOffersVenueResponseModel
from pcapi.serialization.utils import dehumanize_field
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
