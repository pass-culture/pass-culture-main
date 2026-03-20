import typing
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import Favorite
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.shared.price import convert_to_cent


@dataclass
class FavoriteData:
    date: datetime | None
    favorite: Favorite
    is_expired: bool
    price: Decimal | None
    start_date: datetime | None
    start_price: Decimal | None


class FavoriteCoordinates(HttpBodyModel):
    latitude: float | None = None
    longitude: float | None = None


class FavoriteMediationResponse(HttpBodyModel):
    credit: str | None = None
    url: str


class FavoriteOfferResponse(HttpBodyModel):
    id: int
    booking_allowed_datetime: datetime | None = None
    coordinates: FavoriteCoordinates
    date: datetime | None = None
    expense_domains: list[ExpenseDomain]
    external_ticket_office_url: str | None = None
    image: FavoriteMediationResponse | None = None
    is_expired: bool = False
    is_released: bool
    is_sold_out: bool = False
    name: str
    price: int | None = None
    start_date: datetime | None = None
    start_price: int | None = None
    subcategory_id: SubcategoryIdEnum
    venue_name: str

    @classmethod
    def build(cls, favorite_data: FavoriteData) -> typing.Self:
        offer = favorite_data.favorite.offer
        address = offer.venue.offererAddress.address
        venue_name = offer.venue.managingOfferer.name if offer.isDigital else offer.venue.publicName

        if offer.offererAddress:
            address = offer.offererAddress.address
            if offer.offererAddress.label:
                venue_name = offer.offererAddress.label

        return cls(
            id=favorite_data.favorite.id,
            booking_allowed_datetime=offer.bookingAllowedDatetime,
            coordinates=FavoriteCoordinates(latitude=address.latitude, longitude=address.longitude),
            date=favorite_data.date,
            expense_domains=get_expense_domains(offer),
            external_ticket_office_url=offer.externalTicketOfficeUrl,
            image=offer.image,
            is_expired=favorite_data.is_expired,
            is_released=offer.isReleased,
            is_sold_out=offer.isSoldOut,
            name=offer.name,
            price=convert_to_cent(favorite_data.price),
            start_date=favorite_data.start_date,
            start_price=convert_to_cent(favorite_data.start_price),
            subcategory_id=offer.subcategoryId,
            venue_name=venue_name,
        )


class FavoriteResponse(HttpBodyModel):
    id: int
    offer: FavoriteOfferResponse


class PaginatedFavoritesResponse(HttpBodyModel):
    page: int
    nb_favorites: int
    favorites: list[FavoriteResponse]


class FavoriteRequest(HttpBodyModel):
    offer_id: int
