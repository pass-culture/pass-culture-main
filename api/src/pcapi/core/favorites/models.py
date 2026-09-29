from __future__ import annotations  # to type models before their declaration

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
    from pcapi.core.offers.models import Offer
    from pcapi.core.users.models import User


@dataclass
class FavoriteOfferData:
    date: datetime | None
    favorite: FavoriteOffer
    is_expired: bool
    price: Decimal | None
    start_date: datetime | None
    start_price: Decimal | None


class FavoriteOffer(PcObject, Model):
    __tablename__ = "favorite"

    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user: sa_orm.Mapped[User] = sa_orm.relationship("User", foreign_keys=[userId], back_populates="favoriteOffers")

    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False
    )
    offer: sa_orm.Mapped[Offer] = sa_orm.relationship("Offer", foreign_keys=[offerId], back_populates="favorites")

    dateCreated = sa_orm.mapped_column(sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now)

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "offerId",
            name="unique_favorite",
        ),
    )
