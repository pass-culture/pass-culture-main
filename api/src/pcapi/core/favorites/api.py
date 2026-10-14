import typing

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from pcapi import settings
from pcapi.core.artist.models import Artist
from pcapi.core.discoveries import discovery_service
from pcapi.core.discoveries.models import Work
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.batch.trigger_events import track_offer_added_to_favorites_event
from pcapi.core.favorites.models import FavoriteOffer
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError


if typing.TYPE_CHECKING:
    from pcapi.routes.native.v1.serialization.favorites import FavoriteRequest


def _resolve_target(user_id: int, data: "FavoriteRequest") -> tuple[FavoriteOffer, Offer | None]:
    candidate = FavoriteOffer(userId=user_id, work_id=data.work_id, artist_id=data.artist_id)
    if data.offer_id is not None:
        offer, work = discovery_service.get_work_for_offer(data.offer_id, allow_missing_work=True)
        if not (offer.isPublished and offer.venue.managingOfferer.isActive and offer.venue.managingOfferer.isValidated):
            raise ResourceNotFoundError()
        historical = db.session.execute(
            sa.select(FavoriteOffer).where(FavoriteOffer.userId == user_id, FavoriteOffer.offerId == offer.id)
        ).scalar_one_or_none()
        if historical is not None:
            return historical, offer
        if work is not None:
            candidate.work_id = work.id
            candidate.offer_origin_id = offer.id
        else:
            candidate.offerId = offer.id
        return candidate, offer
    if data.work_id is not None and db.session.get(Work, data.work_id) is None:
        raise ResourceNotFoundError()
    if data.artist_id is not None and db.session.get(Artist, data.artist_id) is None:
        raise ResourceNotFoundError()
    return candidate, None


def create_favorite(user: User, data: "FavoriteRequest") -> int:
    db.session.execute(sa.select(User.id).where(User.id == user.id).with_for_update()).scalar_one()
    candidate, offer = _resolve_target(user.id, data)
    if candidate.id is not None:
        return candidate.id
    if candidate.work_id is not None:
        target_column, target_id = FavoriteOffer.work_id, candidate.work_id
    elif candidate.artist_id is not None:
        target_column, target_id = FavoriteOffer.artist_id, candidate.artist_id
    else:
        target_column, target_id = FavoriteOffer.offerId, candidate.offerId
    existing = db.session.execute(
        sa.select(FavoriteOffer).where(FavoriteOffer.userId == user.id, target_column == target_id)
    ).scalar_one_or_none()
    if existing is not None:
        if existing.offer_origin_id is None and candidate.offer_origin_id is not None:
            existing.offer_origin_id = candidate.offer_origin_id
            db.session.flush()
        return existing.id
    if settings.MAX_FAVORITES:
        count = db.session.execute(
            sa.select(sa.func.count()).select_from(FavoriteOffer).where(FavoriteOffer.userId == user.id)
        ).scalar_one()
        if count >= settings.MAX_FAVORITES:
            raise ApiErrors({"code": "MAX_FAVORITES_REACHED"})
    favorite_id = db.session.execute(
        insert(FavoriteOffer)
        .values(
            userId=user.id,
            offerId=candidate.offerId,
            work_id=candidate.work_id,
            artist_id=candidate.artist_id,
            offer_origin_id=candidate.offer_origin_id,
        )
        .on_conflict_do_nothing(
            index_elements=[FavoriteOffer.userId, target_column], index_where=target_column.is_not(None)
        )
        .returning(FavoriteOffer.id)
    ).scalar_one_or_none()
    if favorite_id is None:
        return db.session.execute(
            sa.select(FavoriteOffer.id).where(FavoriteOffer.userId == user.id, target_column == target_id)
        ).scalar_one()
    update_external_user(user)
    if offer is not None:
        track_offer_added_to_favorites_event(user.id, offer)
    return favorite_id
