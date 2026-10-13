import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects.postgresql import insert

from pcapi.core.artist.models import Artist
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


def _discovery_statement() -> sa.Select[tuple[Discovery]]:
    return sa.select(Discovery).options(
        sa_orm.joinedload(Discovery.work).selectinload(Work.artist_links).joinedload(WorkArtist.artist),
        sa_orm.joinedload(Discovery.artist),
    )


def create_discovery(user_id: int, data: "CreateDiscoverySchema") -> Discovery:
    work_id = data.work_id
    artist_id = data.artist_id
    offer_origin_id = None

    if data.offer_id is not None:
        offer = db.session.execute(
            sa.select(Offer)
            .options(sa_orm.joinedload(Offer.product).joinedload(Product.work))
            .where(Offer.id == data.offer_id)
        ).scalar_one_or_none()
        if offer is None:
            raise ResourceNotFoundError()
        if offer.product is None or offer.product.work is None:
            raise ApiErrors({"offerId": ["This offer is not linked to a work."]})
        work_id = offer.product.work.id
        offer_origin_id = offer.id
    elif work_id is not None:
        if db.session.get(Work, work_id) is None:
            raise ResourceNotFoundError()
    elif artist_id is not None and db.session.get(Artist, artist_id) is None:
        raise ResourceNotFoundError()

    target_column = Discovery.work_id if work_id is not None else Discovery.artist_id
    target_id = work_id if work_id is not None else artist_id
    statement = (
        insert(Discovery)
        .values(
            user_id=user_id,
            work_id=work_id,
            artist_id=artist_id,
            offer_origin_id=offer_origin_id,
            **data.model_dump(exclude_none=True, exclude={"work_id", "artist_id", "offer_id"}),
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
