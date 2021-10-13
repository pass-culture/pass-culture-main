from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic.class_validators import validator

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.offers.models import CategoryType
from pcapi.core.users.models import ExpenseDomain
from pcapi.models.offer_type import CategoryNameEnum
from pcapi.routes.native.utils import convert_to_cent
from pcapi.utils.date import format_into_utc_date

from . import BaseModel


# TODO(xordoquy): move common models with offers API
class Coordinates(BaseModel):
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]


# TODO(fseguin): cleanup when native app has been force-updated
class FavoriteCategoryResponse(BaseModel):
    categoryType: CategoryType
    label: str
    name: Optional[CategoryNameEnum]


class FavoriteMediationResponse(BaseModel):
    credit: Optional[str]
    url: str

    class Config:
        orm_mode = True


class FavoriteOfferResponse(BaseModel):
    id: int
    name: str
    category: FavoriteCategoryResponse
    subcategoryId: SubcategoryIdEnum
    externalTicketOfficeUrl: Optional[str]
    image: Optional[FavoriteMediationResponse]
    coordinates: Coordinates
    price: Optional[int] = None
    startPrice: Optional[int] = None
    date: Optional[datetime] = None
    startDate: Optional[datetime] = None
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
        offer.category = {
            "name": offer.subcategory.category_id,
            "label": offer.subcategory.app_label,
            "categoryType": offer.category_type,
        }
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
