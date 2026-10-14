import typing
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils


if typing.TYPE_CHECKING:
    from pcapi.core.artist.models import Artist
    from pcapi.core.discoveries.models import Work
    from pcapi.core.offers.models import Offer
    from pcapi.core.users.models import User


@dataclass
class FavoriteOfferData:
    date: datetime | None
    favorite: "FavoriteOffer"
    is_expired: bool
    price: Decimal | None
    start_date: datetime | None
    start_price: Decimal | None


class FavoriteOffer(PcObject, Model):
    __tablename__ = "favorite"

    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", foreign_keys=[userId], back_populates="favoriteOffers")

    offerId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=True
    )
    offer: sa_orm.Mapped["Offer | None"] = sa_orm.relationship(
        "Offer", foreign_keys=[offerId], back_populates="favorites"
    )
    work_id: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("work.id"), index=True)
    artist_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, sa.ForeignKey("artist.id"), index=True)
    offer_origin_id: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="SET NULL"), index=True
    )
    work: sa_orm.Mapped["Work | None"] = sa_orm.relationship("Work", foreign_keys=[work_id])
    artist: sa_orm.Mapped["Artist | None"] = sa_orm.relationship("Artist", foreign_keys=[artist_id])
    offer_origin: sa_orm.Mapped["Offer | None"] = sa_orm.relationship("Offer", foreign_keys=[offer_origin_id])

    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )

    __table_args__ = (
        sa.CheckConstraint('num_nonnulls("offerId", work_id, artist_id) = 1', name="favorite_exactly_one_target"),
        sa.CheckConstraint("offer_origin_id IS NULL OR work_id IS NOT NULL", name="favorite_origin_requires_work"),
        sa.Index("ix_unique_favorite_offer", "userId", "offerId", unique=True, postgresql_where=offerId.is_not(None)),
        sa.Index("ix_unique_favorite_work", "userId", "work_id", unique=True, postgresql_where=work_id.is_not(None)),
        sa.Index(
            "ix_unique_favorite_artist", "userId", "artist_id", unique=True, postgresql_where=artist_id.is_not(None)
        ),
    )
