from datetime import datetime
from decimal import Decimal

from pydantic.class_validators import validator

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.users.models import ExpenseDomain
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.serialization import BaseModel
from pcapi.utils.date import format_into_utc_date


class Coordinates(BaseModel):
    latitude: Decimal | None
    longitude: Decimal | None


class FavoriteMediationResponse(BaseModel):
    credit: str | None
    url: str

    class Config:
        orm_mode = True


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

    _convert_price = validator("price", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_start_price = validator("startPrice", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, offer):  # type: ignore
        offer.coordinates = {"latitude": offer.venue.latitude, "longitude": offer.venue.longitude}
        offer.expenseDomains = get_expense_domains(offer)
        return super().from_orm(offer)


class FavoriteResponse(BaseModel):
    id: int
    offer: FavoriteOfferResponse

    class Config:
        orm_mode = True


class PaginatedFavoritesResponse(BaseModel):
    page: int
    nbFavorites: int
    favorites: list[FavoriteResponse]

    class Config:
        json_encoders = {datetime: format_into_utc_date}


class FavoriteRequest(BaseModel):
    offerId: int


class FavoritesCountResponse(BaseModel):
    count: int
