import enum
import secrets
import typing

import sqlalchemy.orm as sa_orm

from pcapi.models import Model
from pcapi.models import db
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils
from pcapi.utils.db import MagicEnum


if typing.TYPE_CHECKING:
    from pcapi.core.artist.models import Artist
    from pcapi.core.discoveries.models import Work
    from pcapi.core.users.models import User


class WishlistVisibility(enum.Enum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"


def generate_share_token() -> str:
    return secrets.token_urlsafe(16)


class Wishlist(PcObject, Model):
    __tablename__ = "wishlist"

    user_id = db.Column(db.BigInteger, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    visibility = db.Column(
        MagicEnum(WishlistVisibility, use_values=True),
        nullable=False,
        default=WishlistVisibility.PRIVATE,
        server_default=WishlistVisibility.PRIVATE.value,
    )
    share_token = db.Column(db.Text, nullable=False, unique=True, default=generate_share_token)
    created_at = db.Column(
        db.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=date_utils.get_naive_utc_now,
        onupdate=date_utils.get_naive_utc_now,
        server_default=db.func.now(),
    )

    user: sa_orm.Mapped["User"] = sa_orm.relationship("User")
    items: sa_orm.Mapped[list["WishlistItem"]] = sa_orm.relationship(
        "WishlistItem",
        back_populates="wishlist",
        order_by="(WishlistItem.position, WishlistItem.id)",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        db.CheckConstraint(
            visibility.in_([member.value for member in WishlistVisibility]), name="check_wishlist_visibility"
        ),
        db.CheckConstraint("char_length(btrim(name)) BETWEEN 1 AND 100", name="check_wishlist_name_length"),
    )


class WishlistItem(PcObject, Model):
    __tablename__ = "wishlist_item"

    wishlist_id = db.Column(db.BigInteger, db.ForeignKey("wishlist.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = db.Column(db.BigInteger, db.ForeignKey("work.id", ondelete="CASCADE"), nullable=True, index=True)
    artist_id = db.Column(db.Text, db.ForeignKey("artist.id", ondelete="CASCADE"), nullable=True, index=True)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=db.func.now()
    )

    wishlist: sa_orm.Mapped["Wishlist"] = sa_orm.relationship("Wishlist", back_populates="items")
    work: sa_orm.Mapped["Work | None"] = sa_orm.relationship("Work")
    artist: sa_orm.Mapped["Artist | None"] = sa_orm.relationship("Artist")

    __table_args__ = (
        db.CheckConstraint(
            "(work_id IS NOT NULL) != (artist_id IS NOT NULL)",
            name="check_wishlist_item_exactly_one_target",
        ),
        db.Index(
            "ix_unique_wishlist_item_work",
            "wishlist_id",
            "work_id",
            unique=True,
            postgresql_where=work_id.is_not(None),
        ),
        db.Index(
            "ix_unique_wishlist_item_artist",
            "wishlist_id",
            "artist_id",
            unique=True,
            postgresql_where=artist_id.is_not(None),
        ),
    )
