import datetime
import enum
import logging

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.elements import BinaryExpression

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.users.models import User
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)


class ProductChronicle(PcObject, Base, Model):
    __tablename__ = "product_chronicle"
    productId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chronicleId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("chronicle.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "productId",
            "chronicleId",
            name="unique_product_chronicle_constraint",
        ),
    )


class OfferChronicle(PcObject, Base, Model):
    __tablename__ = "offer_chronicle"
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)
    chronicleId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("chronicle.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "offerId",
            "chronicleId",
            name="unique_offer_chronicle_constraint",
        ),
    )


class ChronicleProductIdentifierType(enum.Enum):
    ALLOCINE_ID = "ALLOCINE_ID"
    EAN = "EAN"
    VISA = "VISA"


class ChronicleClubType(enum.Enum):
    BOOK_CLUB = "BOOK"
    CINE_CLUB = "CINE"


class Chronicle(PcObject, Base, Model, DeactivableMixin):
    __tablename__ = "chronicle"
    age = sa.Column(sa.SmallInteger, nullable=True)
    city = sa.Column(sa.Text(), nullable=True)
    clubType = sa.Column(db_utils.MagicEnum(ChronicleClubType), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    # used to reconciliate data if the form changed on typeform
    identifierChoiceId = sa.Column(sa.Text(), nullable=True)
    email = sa.Column(sa.Text(), nullable=False)
    firstName = sa.Column(sa.Text(), nullable=True)
    externalId = sa.Column(sa.Text(), nullable=False, unique=True)
    isIdentityDiffusible = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    isSocialMediaDiffusible: bool = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    products: sa_orm.Mapped[list["Product"]] = sa_orm.relationship(
        "Product", backref="chronicles", secondary=ProductChronicle.__table__
    )
    offers: sa_orm.Mapped[list["Offer"]] = sa_orm.relationship(
        "Offer", backref="chronicles", secondary=OfferChronicle.__table__
    )
    productIdentifierType: ChronicleProductIdentifierType = sa.Column(
        db_utils.MagicEnum(ChronicleProductIdentifierType), nullable=False
    )
    productIdentifier = sa.Column(sa.Text(), nullable=False, index=True)
    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", foreign_keys=[userId], backref="chronicles")

    __content_ts_vector__ = sa.Column(
        db_utils.TSVector(),
        sa.Computed("to_tsvector('french', content)", persisted=True),
        nullable=False,
        name="__content_ts_vector__",
    )
    __table_args__ = (sa.Index("ix_chronicle_content___ts_vector__", __content_ts_vector__, postgresql_using="gin"),)

    @hybrid_property
    def isPublished(self) -> bool:
        return self.isActive and self.isSocialMediaDiffusible

    @isPublished.expression  # type: ignore[no-redef]
    def isPublished(cls) -> BinaryExpression:
        return sa.and_(cls.isActive.is_(True), cls.isSocialMediaDiffusible.is_(True))

    @property
    def productIdentifierName(self) -> str:
        match self.productIdentifierType:
            case ChronicleProductIdentifierType.ALLOCINE_ID:
                return "ID Allociné"
            case ChronicleProductIdentifierType.EAN:
                return "EAN"
            case ChronicleProductIdentifierType.VISA:
                return "Visa"
            case _:
                raise ValueError()


@sa.event.listens_for(Chronicle, "after_insert")
def after_insert_chronicle(_mapper: sa_orm.Mapper, connection: sa.engine.Connection, target: Chronicle) -> None:
    _increment_product_counts(connection, target, 1)


@sa.event.listens_for(Chronicle, "after_delete")
def after_delete_chronicle(_mapper: sa_orm.Mapper, connection: sa.engine.Connection, target: Chronicle) -> None:
    # SQLAlchemy will not call this event if the object is deleted using a bulk delete
    # (e.g. db.session.execute(sa.delete(Chronicle).where(...)))
    _increment_product_counts(connection, target, -1)


def _increment_product_counts(connection: sa.engine.Connection, target: Chronicle, increment: int) -> None:
    if product_ids := [product.id for product in target.products]:
        connection.execute(
            sa.update(Product)
            .where(Product.id.in_(product_ids))
            .values(chroniclesCount=Product.chroniclesCount + increment)
        )
