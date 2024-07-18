from datetime import datetime
from decimal import Decimal

from pydantic.v1.class_validators import validator

from pcapi.core.categories.subcategories_v2 import SubcategoryIdEnum
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import ExpenseDomain
from pcapi.routes.serialization import BaseModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.utils.date import format_into_utc_date
from pydantic import ConfigDict


class Coordinates(BaseModel):
    latitude: Decimal | None
    longitude: Decimal | None


class FavoriteMediationResponse(BaseModel):
    credit: str | None
    url: str
    model_config = ConfigDict(from_attributes=True)


class FavoriteOfferResponse(BaseModel):
    id: int
    name: str
    subcategoryId: SubcategoryIdEnum
    externalTicketOfficeUrl: str | None
    image: FavoriteMediationResponse | None
    coordinates: Coordinates
    price: int | None = None
    startPrice: int | None = None
    date: datetime | None = None
    startDate: datetime | None = None
    isExpired: bool = False
    expenseDomains: list[ExpenseDomain]
    isReleased: bool
    isSoldOut: bool = False
    venueName: str

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_start_price = validator("startPrice", pre=True, allow_reuse=True)(convert_to_cent)
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, offer: Offer) -> "FavoriteOfferResponse":
        offer.coordinates = {"latitude": offer.venue.latitude, "longitude": offer.venue.longitude}
        offer.venueName = offer.venue.managingOfferer.name if offer.isDigital else offer.venue.common_name
        offer.expenseDomains = get_expense_domains(offer)
        return super().from_orm(offer)


class FavoriteResponse(BaseModel):
    id: int
    offer: FavoriteOfferResponse
    model_config = ConfigDict(from_attributes=True)


class PaginatedFavoritesResponse(BaseModel):
    page: int
    nbFavorites: int
    favorites: list[FavoriteResponse]
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={datetime: format_into_utc_date})


class FavoriteRequest(BaseModel):
    offerId: int


class FavoritesCountResponse(BaseModel):
    count: int
