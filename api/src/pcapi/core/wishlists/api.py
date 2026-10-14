import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects.postgresql import insert

from pcapi.core.artist.models import Artist
from pcapi.core.discoveries import discovery_service
from pcapi.core.discoveries.models import Work
from pcapi.core.discoveries.models import WorkArtist
from pcapi.core.wishlists.models import Wishlist
from pcapi.core.wishlists.models import WishlistItem
from pcapi.core.wishlists.models import WishlistVisibility
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.utils import date as date_utils


if typing.TYPE_CHECKING:
    from pcapi.routes.native.v1.serialization.wishlists import AddWishlistItemSchema
    from pcapi.routes.native.v1.serialization.wishlists import CreateWishlistSchema
    from pcapi.routes.native.v1.serialization.wishlists import UpdateWishlistSchema


def _wishlist_statement() -> sa.Select[tuple[Wishlist]]:
    return sa.select(Wishlist).options(
        sa_orm.joinedload(Wishlist.user),
        sa_orm.selectinload(Wishlist.items).options(
            sa_orm.joinedload(WishlistItem.work).selectinload(Work.artist_links).joinedload(WorkArtist.artist),
            sa_orm.joinedload(WishlistItem.artist),
        ),
    )


def _summary_statement() -> sa.Select[tuple[Wishlist]]:
    return sa.select(Wishlist).options(sa_orm.joinedload(Wishlist.user), sa_orm.selectinload(Wishlist.items))


def _get_owned_wishlist(user_id: int, wishlist_id: int) -> Wishlist:
    wishlist = db.session.execute(
        _wishlist_statement().where(Wishlist.id == wishlist_id, Wishlist.user_id == user_id)
    ).scalar_one_or_none()
    if wishlist is None:
        raise ResourceNotFoundError()
    return wishlist


def create_wishlist(user_id: int, data: "CreateWishlistSchema") -> Wishlist:
    wishlist = Wishlist(user_id=user_id, **data.model_dump())
    db.session.add(wishlist)
    db.session.flush()
    return _get_owned_wishlist(user_id, wishlist.id)


def update_wishlist(user_id: int, wishlist_id: int, data: "UpdateWishlistSchema") -> Wishlist:
    wishlist = _get_owned_wishlist(user_id, wishlist_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(wishlist, field, value)
    db.session.flush()
    return wishlist


def delete_wishlist(user_id: int, wishlist_id: int) -> None:
    deleted_id = db.session.execute(
        sa.delete(Wishlist).where(Wishlist.id == wishlist_id, Wishlist.user_id == user_id).returning(Wishlist.id)
    ).scalar_one_or_none()
    if deleted_id is None:
        raise ResourceNotFoundError()


def get_user_wishlists(user_id: int, page: int, limit: int) -> list[Wishlist]:
    return list(
        db.session.execute(
            _summary_statement()
            .where(Wishlist.user_id == user_id)
            .order_by(Wishlist.updated_at.desc(), Wishlist.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).scalars()
    )


def get_visible_wishlist(user_id: int, wishlist_id: int) -> Wishlist:
    wishlist = db.session.execute(
        _wishlist_statement().where(
            Wishlist.id == wishlist_id,
            sa.or_(Wishlist.user_id == user_id, Wishlist.visibility == WishlistVisibility.PUBLIC),
        )
    ).scalar_one_or_none()
    if wishlist is None:
        raise ResourceNotFoundError()
    return wishlist


def get_wishlist_by_token(share_token: str) -> Wishlist:
    wishlist = db.session.execute(
        _wishlist_statement().where(
            Wishlist.share_token == share_token, Wishlist.visibility != WishlistVisibility.PRIVATE
        )
    ).scalar_one_or_none()
    if wishlist is None:
        raise ResourceNotFoundError()
    return wishlist


def search_public_wishlists(query: str, page: int, limit: int) -> list[Wishlist]:
    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return list(
        db.session.execute(
            _summary_statement()
            .where(
                Wishlist.visibility == WishlistVisibility.PUBLIC,
                Wishlist.name.ilike(f"%{escaped}%", escape="\\"),
            )
            .order_by(Wishlist.updated_at.desc(), Wishlist.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).scalars()
    )


def add_item(user_id: int, wishlist_id: int, data: "AddWishlistItemSchema") -> Wishlist:
    wishlist = _get_owned_wishlist(user_id, wishlist_id)
    work_id = data.work_id
    artist_id = data.artist_id

    if data.offer_id is not None:
        _, work = discovery_service.get_work_for_offer(data.offer_id)
        work_id = work.id
    elif work_id is not None:
        if db.session.get(Work, work_id) is None:
            raise ResourceNotFoundError()
    elif artist_id is not None and db.session.get(Artist, artist_id) is None:
        raise ResourceNotFoundError()

    target_column = WishlistItem.work_id if work_id is not None else WishlistItem.artist_id
    next_position = (
        sa.select(sa.func.coalesce(sa.func.max(WishlistItem.position) + 1, 0))
        .where(WishlistItem.wishlist_id == wishlist.id)
        .scalar_subquery()
    )
    db.session.execute(
        insert(WishlistItem)
        .values(wishlist_id=wishlist.id, work_id=work_id, artist_id=artist_id, position=next_position)
        .on_conflict_do_nothing(
            index_elements=[WishlistItem.wishlist_id, target_column], index_where=target_column.is_not(None)
        )
    )
    wishlist.updated_at = date_utils.get_naive_utc_now()
    db.session.flush()
    db.session.expire(wishlist)
    return _get_owned_wishlist(user_id, wishlist_id)


def remove_item(user_id: int, wishlist_id: int, item_id: int) -> None:
    wishlist = _get_owned_wishlist(user_id, wishlist_id)
    deleted_id = db.session.execute(
        sa.delete(WishlistItem)
        .where(WishlistItem.id == item_id, WishlistItem.wishlist_id == wishlist.id)
        .returning(WishlistItem.id)
    ).scalar_one_or_none()
    if deleted_id is None:
        raise ResourceNotFoundError()
    wishlist.updated_at = date_utils.get_naive_utc_now()
    db.session.flush()


def reorder_items(user_id: int, wishlist_id: int, item_ids: list[int]) -> Wishlist:
    wishlist = _get_owned_wishlist(user_id, wishlist_id)
    items_by_id = {item.id: item for item in wishlist.items}
    if len(item_ids) != len(set(item_ids)) or set(item_ids) != set(items_by_id):
        raise ApiErrors({"itemIds": ["itemIds must contain every item of the wishlist exactly once."]})
    for position, item_id in enumerate(item_ids):
        items_by_id[item_id].position = position
    wishlist.updated_at = date_utils.get_naive_utc_now()
    db.session.flush()
    db.session.expire(wishlist)
    return _get_owned_wishlist(user_id, wishlist_id)
