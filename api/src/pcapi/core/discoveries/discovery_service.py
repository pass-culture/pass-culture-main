import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects.postgresql import insert

from pcapi.core.artist.models import Artist
from pcapi.core.bookings.models import Booking
from pcapi.core.discoveries.models import Discovery
from pcapi.core.discoveries.models import Work
from pcapi.core.discoveries.models import WorkArtist
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError


if typing.TYPE_CHECKING:
    from pcapi.routes.native.v1.serialization.discoveries import CreateDiscoverySchema
    from pcapi.routes.native.v1.serialization.discoveries import UpdateDiscoverySchema


def _discovery_statement() -> sa.Select[tuple[Discovery]]:
    return sa.select(Discovery).options(
        sa_orm.joinedload(Discovery.work).selectinload(Work.artist_links).joinedload(WorkArtist.artist),
        sa_orm.joinedload(Discovery.artist),
    )


def get_work_for_offer(offer_id: int) -> tuple[Offer, Work]:
    offer = db.session.execute(
        sa.select(Offer)
        .options(sa_orm.joinedload(Offer.work), sa_orm.joinedload(Offer.product).joinedload(Product.work))
        .where(Offer.id == offer_id)
    ).scalar_one_or_none()
    if offer is None:
        raise ResourceNotFoundError()
    work = offer.work or (offer.product.work if offer.product is not None else None)
    if work is None:
        raise ApiErrors({"offerId": ["This offer is not linked to a work."]})
    return offer, work


def create_discovery(user_id: int, data: "CreateDiscoverySchema") -> Discovery:
    work_id = data.work_id
    artist_id = data.artist_id
    offer_origin_id = None

    if data.offer_id is not None:
        offer, work = get_work_for_offer(data.offer_id)
        work_id = work.id
        offer_origin_id = offer.id
    elif work_id is not None:
        if db.session.get(Work, work_id) is None:
            raise ResourceNotFoundError()
    elif artist_id is not None and db.session.get(Artist, artist_id) is None:
        raise ResourceNotFoundError()

    target_column = Discovery.work_id if work_id is not None else Discovery.artist_id
    target_id = work_id if work_id is not None else artist_id
    emotion_values = [emotion.value for emotion in data.emotions] if data.emotions is not None else None
    statement = (
        insert(Discovery)
        .values(
            user_id=user_id,
            work_id=work_id,
            artist_id=artist_id,
            offer_origin_id=offer_origin_id,
            emotions=emotion_values,
            **data.model_dump(exclude_none=True, exclude={"work_id", "artist_id", "offer_id", "emotions"}),
        )
        .on_conflict_do_nothing(
            index_elements=[Discovery.user_id, target_column], index_where=target_column.is_not(None)
        )
        .returning(Discovery.id)
    )
    db.session.execute(statement).scalar_one_or_none()
    return db.session.execute(
        _discovery_statement().where(Discovery.user_id == user_id, target_column == target_id)
    ).scalar_one()


def create_discoveries_for_booking(booking: Booking) -> None:
    offer = db.session.execute(
        sa.select(Offer)
        .options(
            sa_orm.joinedload(Offer.work).selectinload(Work.artist_links),
            sa_orm.joinedload(Offer.product).options(
                sa_orm.joinedload(Product.work).selectinload(Work.artist_links),
                sa_orm.selectinload(Product.artistLinks),
            ),
            sa_orm.selectinload(Offer.artistOfferLinks),
        )
        .where(Offer.id == booking.stock.offerId)
    ).scalar_one_or_none()
    if offer is None:
        return

    work = offer.work or (offer.product.work if offer.product is not None else None)
    artist_ids = {link.artist_id for link in offer.artistOfferLinks if link.artist_id is not None}
    if offer.product is not None:
        artist_ids.update(link.artist_id for link in offer.product.artistLinks)
    if work is not None:
        artist_ids.update(link.artist_id for link in work.artist_links)

    targets: list[tuple[int | None, str | None]] = []
    if work is not None:
        targets.append((work.id, None))
    targets.extend((None, artist_id) for artist_id in sorted(artist_ids))

    for work_id, artist_id in targets:
        target_column = Discovery.work_id if work_id is not None else Discovery.artist_id
        db.session.execute(
            insert(Discovery)
            .values(
                user_id=booking.userId,
                work_id=work_id,
                artist_id=artist_id,
                offer_origin_id=offer.id,
            )
            .on_conflict_do_nothing(
                index_elements=[Discovery.user_id, target_column], index_where=target_column.is_not(None)
            )
        )


def update_discovery(user_id: int, discovery_id: int, data: "UpdateDiscoverySchema") -> Discovery:
    discovery = db.session.execute(
        _discovery_statement().where(Discovery.id == discovery_id, Discovery.user_id == user_id)
    ).scalar_one_or_none()
    if discovery is None:
        raise ResourceNotFoundError()
    updated_values = data.model_dump(exclude_unset=True)
    if data.emotions is not None:
        updated_values["emotions"] = [emotion.value for emotion in data.emotions]
    for field, value in updated_values.items():
        setattr(discovery, field, value)
    db.session.flush()
    return discovery


def delete_discovery(user_id: int, discovery_id: int) -> None:
    deleted_id = db.session.execute(
        sa.delete(Discovery).where(Discovery.id == discovery_id, Discovery.user_id == user_id).returning(Discovery.id)
    ).scalar_one_or_none()
    if deleted_id is None:
        raise ResourceNotFoundError()


def get_user_discoveries(user_id: int, page: int = 1, limit: int = 20) -> list[Discovery]:
    if page < 1 or not 1 <= limit <= 100:
        raise ApiErrors({"pagination": ["page must be positive and limit must be between 1 and 100."]})
    return list(
        db.session.execute(
            _discovery_statement()
            .where(Discovery.user_id == user_id)
            .order_by(Discovery.discovery_date.desc(), Discovery.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).scalars()
    )
