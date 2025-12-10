import enum
import typing
import uuid
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.db import MagicEnum


if typing.TYPE_CHECKING:
    from pcapi.core.offers.models import Product


class ArtistType(enum.Enum):
    """
    A link Artist <> Product also bears a type
    An artist can be an author or a musician for different products
    """

    AUTHOR = "author"
    PERFORMER = "performer"


class ArtistProductLink(PcObject, Model):
    __tablename__ = "artist_product_link"

    artist_id: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.Text, sa.ForeignKey("artist.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True
    )
    artist_type: sa_orm.Mapped[ArtistType | None] = sa_orm.mapped_column(MagicEnum(ArtistType), nullable=True)
    date_created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    date_modified: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, onupdate=sa.func.now()
    )


class Artist(Model):
    __tablename__ = "artist"
    id: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.Text, primary_key=True, nullable=False, default=lambda _: str(uuid.uuid4())
    )
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, index=True)
    computed_image: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    image: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    image_author: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    image_license: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    image_license_url: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    date_created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    date_modified: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, onupdate=sa.func.now()
    )
    is_blacklisted: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.false(), default=False
    )
    wikidata_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    wikipedia_url: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    biography: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    products: sa_orm.Mapped[list["Product"]] = sa_orm.relationship(
        "Product", back_populates="artists", secondary=ArtistProductLink.__table__
    )
    aliases: sa_orm.Mapped[list["ArtistAlias"]] = sa_orm.relationship(
        "ArtistAlias", foreign_keys="ArtistAlias.artist_id", back_populates="artist"
    )

    is_eligible_for_search: sa_orm.Mapped["bool"] = sa_orm.query_expression()

    __table_args__ = (
        sa.Index(
            "ix_artist_trgm_unaccent_name",
            sa.func.immutable_unaccent("name"),
            postgresql_using="gin",
            postgresql_ops={
                "description": "gin_trgm_ops",
            },
        ),
        sa.Index(
            "ix_unique_artist_wikidata_id",
            "wikidata_id",
            unique=True,
        ),
    )

    @property
    def thumbUrl(self) -> str | None:
        return self.image or self.computed_image


class ArtistAlias(PcObject, Model):
    """
    The data in this table is used by the data team
    to reconcile artists across different sources (e.g. Wikidata)
    Some field may seem incongruous, but they are useful to have
    in order to be able to compare the data from different sources
    """

    __tablename__ = "artist_alias"
    artist_id: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.Text, sa.ForeignKey("artist.id", ondelete="CASCADE"), nullable=False, index=True
    )
    artist: sa_orm.Mapped[Artist] = sa_orm.relationship(Artist, foreign_keys=[artist_id], back_populates="aliases")
    artist_alias_name: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    artist_cluster_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    artist_type: sa_orm.Mapped[ArtistType | None] = sa_orm.mapped_column(MagicEnum(ArtistType), nullable=True)
    artist_wiki_data_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    offer_category_id: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    date_created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    date_modified: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, onupdate=sa.func.now()
    )
    __table_args__ = (
        sa.Index(
            "ix_artist_alias_trgm_unaccent_name",
            sa.func.immutable_unaccent("artist_alias_name"),
            postgresql_using="gin",
            postgresql_ops={
                "description": "gin_trgm_ops",
            },
        ),
    )
