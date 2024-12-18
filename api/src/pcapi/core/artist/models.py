import enum
import typing
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Base
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


class Artist(PcObject, Base, Model):
    id = sa.Column(sa.Text, primary_key=True, nullable=False, default=lambda _: uuid.uuid4().hex)
    name = sa.Column(sa.Text, nullable=False, index=True)
    description = sa.Column(sa.Text)
    image = sa.Column(sa.Text)
    image_license = sa.Column(sa.Text)
    image_license_url = sa.Column(sa.Text)

    products: list[sa_orm.Mapped["Product"]] = sa_orm.relationship(
        "Product", backref="artists", secondary="artist_product_link"
    )


class ArtistAlias(PcObject, Base, Model):
    """
    The data in this table is used by the data team
    to reconcile artists across different sources (e.g. Wikidata)
    Some field may seem incongruous, but they are useful to have
    in order to be able to compare the data from different sources
    """

    artist_id = sa.Column(sa.Text, sa.ForeignKey("artist.id", ondelete="CASCADE"), nullable=False, index=True)
    artist_alias_name = sa.Column(sa.Text)
    artist_cluster_id = sa.Column(sa.Text)
    artist_type = sa.Column(MagicEnum(ArtistType))
    artist_wiki_data_id = sa.Column(sa.Text)
    offer_category_id = sa.Column(sa.Text)


class ArtistProductLink(PcObject, Base, Model):
    __tablename__ = "artist_product_link"

    artist_id = sa.Column(sa.Text, sa.ForeignKey("artist.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = sa.Column(sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True)

    artist_type = sa.Column(MagicEnum(ArtistType))
