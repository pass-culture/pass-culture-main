import enum
import typing
from datetime import date

import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList

from pcapi.models import Model
from pcapi.models import db
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils
from pcapi.utils.db import MagicEnum


if typing.TYPE_CHECKING:
    from pcapi.core.artist.models import Artist
    from pcapi.core.offers.models import Offer
    from pcapi.core.offers.models import Product
    from pcapi.core.users.models import User


class WorkMediaType(enum.Enum):
    BOOK = "book"
    FILM = "film"
    MUSIC = "music"
    PERFORMING_ART = "performing_art"
    VISUAL_ART = "visual_art"
    VIDEO_GAME = "video_game"
    OTHER = "other"


class DiscoveryEmotion(enum.Enum):
    INTRIGUED = "intrigu\u00e9"
    AMAZED = "\u00e9merveill\u00e9"
    MOVED = "touch\u00e9"
    SURPRISED = "surpris"
    SHAKEN = "bouscul\u00e9"
    INDIFFERENT = "indiff\u00e9rent"


# Model is the project's typed alias for db.Model; PcObject provides a BigInteger id.
class Work(PcObject, Model):
    __tablename__ = "work"

    offer_id = db.Column(db.BigInteger, db.ForeignKey("offer.id", ondelete="SET NULL"), nullable=True, unique=True)
    title = db.Column(db.String, nullable=False)
    media_type = db.Column(MagicEnum(WorkMediaType, use_values=True), nullable=False)
    release_year = db.Column(db.BigInteger, nullable=True)
    visual_url = db.Column(db.String, nullable=True)
    external_ids = db.Column(
        MutableDict.as_mutable(postgresql.JSONB), nullable=False, default=dict, server_default="{}"
    )

    products: sa_orm.Mapped[list["Product"]] = sa_orm.relationship("Product", back_populates="work")
    offer: sa_orm.Mapped["Offer | None"] = sa_orm.relationship("Offer", back_populates="work", uselist=False)
    artist_links: sa_orm.Mapped[list["WorkArtist"]] = sa_orm.relationship(
        "WorkArtist", back_populates="work", cascade="all, delete-orphan", passive_deletes=True
    )
    discoveries: sa_orm.Mapped[list["Discovery"]] = sa_orm.relationship(
        "Discovery", back_populates="work", passive_deletes="all"
    )

    __table_args__ = (
        db.CheckConstraint(media_type.in_([member.value for member in WorkMediaType]), name="work_media_type"),
    )


class WorkArtist(Model):
    __tablename__ = "work_artist"

    work_id = db.Column(db.BigInteger, db.ForeignKey("work.id", ondelete="CASCADE"), primary_key=True)
    # Artist already uses text UUIDs, not the BigInteger ids provided by PcObject.
    artist_id = db.Column(db.Text, db.ForeignKey("artist.id", ondelete="CASCADE"), primary_key=True, index=True)
    role = db.Column(db.String, nullable=False)

    work: sa_orm.Mapped["Work"] = sa_orm.relationship("Work", back_populates="artist_links")
    artist: sa_orm.Mapped["Artist"] = sa_orm.relationship("Artist", back_populates="work_links")


class Discovery(PcObject, Model):
    __tablename__ = "discovery"

    user_id = db.Column(db.BigInteger, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = db.Column(db.BigInteger, db.ForeignKey("work.id"), nullable=True, index=True)
    artist_id = db.Column(db.Text, db.ForeignKey("artist.id"), nullable=True, index=True)
    offer_origin_id = db.Column(
        db.BigInteger, db.ForeignKey("offer.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Pass the callable so the default is computed at insertion, not at import time.
    discovery_date = db.Column(db.Date, nullable=False, default=date.today, server_default=db.func.current_date())
    format_context = db.Column(db.String, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    emotions = db.Column(MutableList.as_mutable(postgresql.ARRAY(db.Text)), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=db.func.now()
    )

    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", back_populates="discoveries")
    work: sa_orm.Mapped["Work | None"] = sa_orm.relationship("Work", back_populates="discoveries")
    artist: sa_orm.Mapped["Artist | None"] = sa_orm.relationship("Artist", back_populates="discoveries")
    offer_origin: sa_orm.Mapped["Offer | None"] = sa_orm.relationship("Offer")

    __table_args__ = (
        # IS NOT NULL always yields a boolean, so SQL NULL cannot bypass this CHECK.
        # XOR accepts exactly one target: neither both targets nor no target.
        db.CheckConstraint(
            "(work_id IS NOT NULL) != (artist_id IS NOT NULL)",
            name="check_discovery_exactly_one_target",
        ),
        db.CheckConstraint(
            "emotions IS NULL OR (array_position(emotions, NULL) IS NULL AND emotions <@ "
            "ARRAY['intrigu\u00e9', '\u00e9merveill\u00e9', 'touch\u00e9', 'surpris', 'bouscul\u00e9', "
            "'indiff\u00e9rent']::text[])",
            name="check_discovery_emotions",
        ),
        db.Index(
            "ix_unique_discovery_user_work", "user_id", "work_id", unique=True, postgresql_where=work_id.is_not(None)
        ),
        db.Index(
            "ix_unique_discovery_user_artist",
            "user_id",
            "artist_id",
            unique=True,
            postgresql_where=artist_id.is_not(None),
        ),
    )
