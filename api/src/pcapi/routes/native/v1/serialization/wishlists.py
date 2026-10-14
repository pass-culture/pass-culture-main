import typing
from datetime import datetime

from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

from pcapi.core.wishlists import models
from pcapi.routes.native.v1.serialization.discoveries import ArtistResponseSchema
from pcapi.routes.native.v1.serialization.discoveries import WorkResponseSchema
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


def _strip_name(value: str | None) -> str:
    if value is None or not value.strip():
        raise ValueError("name cannot be empty")
    return value.strip()


class CreateWishlistSchema(HttpBodyModel):
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    visibility: models.WishlistVisibility = models.WishlistVisibility.PRIVATE

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        return _strip_name(value)


class UpdateWishlistSchema(HttpBodyModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    visibility: models.WishlistVisibility | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        return _strip_name(value)

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value: models.WishlistVisibility | None) -> models.WishlistVisibility:
        if value is None:
            raise ValueError("visibility cannot be null")
        return value


class AddWishlistItemSchema(HttpBodyModel):
    work_id: int | None = Field(default=None, gt=0, le=2**63 - 1)
    artist_id: str | None = Field(default=None, min_length=1)
    offer_id: int | None = Field(default=None, gt=0, le=2**63 - 1)

    @model_validator(mode="after")
    def validate_exactly_one_target(self) -> typing.Self:
        if sum(target is not None for target in (self.work_id, self.artist_id, self.offer_id)) != 1:
            raise ValueError("Exactly one of work_id, artist_id or offer_id is required")
        return self


class ReorderWishlistItemsSchema(HttpBodyModel):
    item_ids: list[int]


class WishlistsQuerySchema(HttpQueryParamsModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class WishlistSearchQuerySchema(WishlistsQuerySchema):
    q: str = Field(min_length=2, max_length=100)


class WishlistOwnerSchema(HttpBodyModel):
    id: int
    first_name: str | None


class WishlistItemResponseSchema(HttpBodyModel):
    id: int
    position: int
    work: WorkResponseSchema | None
    artist: ArtistResponseSchema | None

    @classmethod
    def build(cls, item: models.WishlistItem) -> typing.Self:
        return cls(
            id=item.id,
            position=item.position,
            work=WorkResponseSchema.build(item.work) if item.work else None,
            artist=ArtistResponseSchema.model_validate(item.artist) if item.artist else None,
        )


class WishlistSummaryResponseSchema(HttpBodyModel):
    id: int
    name: str
    description: str | None
    visibility: models.WishlistVisibility
    owner: WishlistOwnerSchema
    items_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def build(cls, wishlist: models.Wishlist) -> typing.Self:
        return cls(
            id=wishlist.id,
            name=wishlist.name,
            description=wishlist.description,
            visibility=wishlist.visibility,
            owner=WishlistOwnerSchema(id=wishlist.user.id, first_name=wishlist.user.firstName),
            items_count=len(wishlist.items),
            created_at=wishlist.created_at,
            updated_at=wishlist.updated_at,
        )


class WishlistResponseSchema(WishlistSummaryResponseSchema):
    is_owner: bool
    # Only exposed to the owner, who is the one sharing the link.
    share_token: str | None
    items: list[WishlistItemResponseSchema]

    @classmethod
    def build_for(cls, wishlist: models.Wishlist, user_id: int | None) -> typing.Self:
        is_owner = user_id is not None and wishlist.user_id == user_id
        return cls(
            **WishlistSummaryResponseSchema.build(wishlist).model_dump(),
            is_owner=is_owner,
            share_token=wishlist.share_token if is_owner else None,
            items=[WishlistItemResponseSchema.build(item) for item in wishlist.items],
        )


class WishlistsResponseSchema(HttpBodyModel):
    page: int
    limit: int
    wishlists: list[WishlistSummaryResponseSchema]
