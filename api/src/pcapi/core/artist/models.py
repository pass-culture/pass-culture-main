import enum
import typing
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.db import MagicEnum


if typing.TYPE_CHECKING:
    from pcapi.core.products.models import Product


class ArtistType(enum.Enum):
    """
    A link Artist <> Product also bears a type
    An artist can be an author or a musician for different products
    """

    AUTHOR = "author"
    PERFORMER = "performer"


class ArtistProductLink(PcObject, Model):
    __tablename__ = "artist_product_link"

    artist_id = sa_orm.mapped_column(
        sa.Text, sa.ForeignKey("artist.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True
    )
    artist_type = sa_orm.mapped_column(MagicEnum(ArtistType))
    date_created = sa_orm.mapped_column(sa.DateTime, nullable=False, server_default=sa.func.now())
    date_modified = sa_orm.mapped_column(sa.DateTime, nullable=True, onupdate=sa.func.now())


class Artist(PcObject, Model):
    __tablename__ = "artist"
    id = sa_orm.mapped_column(sa.Text, primary_key=True, nullable=False, default=lambda _: str(uuid.uuid4()))
    name = sa_orm.mapped_column(sa.Text, nullable=False, index=True)
    computed_image = sa_orm.mapped_column(sa.Text)
    description = sa_orm.mapped_column(sa.Text)
    image = sa_orm.mapped_column(sa.Text)
    image_author = sa_orm.mapped_column(sa.Text)
    image_license = sa_orm.mapped_column(sa.Text)
    image_license_url = sa_orm.mapped_column(sa.Text)
    date_created = sa_orm.mapped_column(sa.DateTime, nullable=False, server_default=sa.func.now())
    date_modified = sa_orm.mapped_column(sa.DateTime, nullable=True, onupdate=sa.func.now())
    is_blacklisted = sa_orm.mapped_column(sa.Boolean, nullable=False, server_default=sa.false(), default=False)

    products: sa_orm.Mapped[list["Product"]] = sa_orm.relationship(
        "Product", backref="artists", secondary=ArtistProductLink.__table__
    )
    aliases: sa_orm.Mapped[list["ArtistAlias"]] = sa_orm.relationship("ArtistAlias", backref="artist")

    __table_args__ = (
        sa.Index(
            "ix_artist_trgm_unaccent_name",
            sa.func.immutable_unaccent("name"),
            postgresql_using="gin",
            postgresql_ops={
                "description": "gin_trgm_ops",
            },
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
    artist_id = sa_orm.mapped_column(
        sa.Text, sa.ForeignKey("artist.id", ondelete="CASCADE"), nullable=False, index=True
    )
    artist_alias_name = sa_orm.mapped_column(sa.Text)
    artist_cluster_id = sa_orm.mapped_column(sa.Text)
    artist_type = sa_orm.mapped_column(MagicEnum(ArtistType))
    artist_wiki_data_id = sa_orm.mapped_column(sa.Text)
    offer_category_id = sa_orm.mapped_column(sa.Text)
    date_created = sa_orm.mapped_column(sa.DateTime, nullable=False, server_default=sa.func.now())
    date_modified = sa_orm.mapped_column(sa.DateTime, nullable=True, onupdate=sa.func.now())
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
