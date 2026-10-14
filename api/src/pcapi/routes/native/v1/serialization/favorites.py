import typing
from datetime import datetime

from pydantic import Field
from pydantic import model_validator

from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.favorites.models import FavoriteOfferData
from pcapi.core.finance.utils import to_cents
from pcapi.core.offers.api import get_expense_domains
from pcapi.core.users.models import ExpenseDomain
from pcapi.routes.native.v1.serialization.discoveries import ArtistResponseSchema
from pcapi.routes.native.v1.serialization.discoveries import WorkResponseSchema
from pcapi.routes.serialization import HttpBodyModel


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
    def build(cls, favorite_data: FavoriteOfferData) -> typing.Self:
        offer = favorite_data.favorite.offer or favorite_data.favorite.offer_origin
        if offer is None:
            raise ValueError("Favorite has no offer")
        address = offer.venue.offererAddress.address
        venue_name = offer.venue.managingOfferer.name if offer.isDigital else offer.venue.publicName

        if offer.offererAddress:
            address = offer.offererAddress.address
            if offer.offererAddress.label:
                venue_name = offer.offererAddress.label

        return cls(
            id=offer.id,
            booking_allowed_datetime=offer.bookingAllowedDatetime,
            coordinates=FavoriteCoordinates(latitude=float(address.latitude), longitude=float(address.longitude)),
            date=favorite_data.date,
            expense_domains=get_expense_domains(offer),
            external_ticket_office_url=offer.externalTicketOfficeUrl,
            image=FavoriteMediationResponse(credit=offer.image.credit, url=offer.image.url) if offer.image else None,
            is_expired=favorite_data.is_expired,
            is_released=offer.isReleased,
            is_sold_out=offer.isSoldOut,
            name=offer.name,
            price=to_cents(favorite_data.price) if favorite_data.price is not None else None,
            start_date=favorite_data.start_date,
            start_price=to_cents(favorite_data.start_price) if favorite_data.start_price is not None else None,
            subcategory_id=offer.subcategoryId,  # type: ignore [arg-type]
            venue_name=venue_name,
        )


class FavoriteResponse(HttpBodyModel):
    id: int
    created_at: datetime
    offer: FavoriteOfferResponse | None
    work: WorkResponseSchema | None
    artist: ArtistResponseSchema | None

    @classmethod
    def build(cls, favorite_data: FavoriteOfferData) -> typing.Self:
        favorite = favorite_data.favorite
        offer = favorite.offer or favorite.offer_origin
        return cls(
            id=favorite.id,
            created_at=favorite.dateCreated,
            offer=FavoriteOfferResponse.build(favorite_data) if offer is not None and offer.isPublished else None,
            work=WorkResponseSchema.build(favorite.work) if favorite.work is not None else None,
            artist=ArtistResponseSchema.model_validate(favorite.artist) if favorite.artist is not None else None,
        )


class PaginatedFavoritesResponse(HttpBodyModel):
    page: int
    nb_favorites: int
    favorites: list[FavoriteResponse]


class FavoriteRequest(HttpBodyModel):
    offer_id: int | None = None
    work_id: int | None = Field(default=None, gt=0, le=2**63 - 1)
    artist_id: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_exactly_one_target(self) -> typing.Self:
        if sum(target is not None for target in (self.offer_id, self.work_id, self.artist_id)) != 1:
            raise ValueError("Exactly one of offer_id, work_id or artist_id is required")
        return self
