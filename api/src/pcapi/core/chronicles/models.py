import datetime
import enum
import logging
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.elements import ColumnElement

from pcapi.core.history.constants import ACTION_HISTORY_ORDER_BY
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.users.models import User
from pcapi.models import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from pcapi.core.history.models import ActionHistory


class ProductChronicle(PcObject, Model):
    __tablename__ = "product_chronicle"
    productId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chronicleId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("chronicle.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "productId",
            "chronicleId",
            name="unique_product_chronicle_constraint",
        ),
    )


class OfferChronicle(PcObject, Model):
    __tablename__ = "offer_chronicle"
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chronicleId: sa_orm.Mapped[int] = sa_orm.mapped_column(
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


class Chronicle(PcObject, Model, DeactivableMixin):
    __tablename__ = "chronicle"
    age: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.SmallInteger, nullable=True)
    city: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    clubType: sa_orm.Mapped[ChronicleClubType] = sa_orm.mapped_column(
        db_utils.MagicEnum(ChronicleClubType), nullable=False
    )
    content: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    # used to reconciliate data if the form changed on typeform
    identifierChoiceId: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    email: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)
    firstName: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    externalId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False, unique=True)
    isIdentityDiffusible: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    isSocialMediaDiffusible: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    products: sa_orm.Mapped[list["Product"]] = sa_orm.relationship(
        "Product", back_populates="chronicles", secondary=ProductChronicle.__table__
    )
    offers: sa_orm.Mapped[list["Offer"]] = sa_orm.relationship(
        "Offer", back_populates="chronicles", secondary=OfferChronicle.__table__
    )
    productIdentifierType: sa_orm.Mapped[ChronicleProductIdentifierType] = sa_orm.mapped_column(
        db_utils.MagicEnum(ChronicleProductIdentifierType), nullable=False
    )
    productIdentifier = sa_orm.mapped_column(sa.Text(), nullable=False, index=True)
    userId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), index=True, nullable=True
    )
    user: sa_orm.Mapped["User | None"] = sa_orm.relationship("User", foreign_keys=[userId], back_populates="chronicles")

    _content_ts_vector: sa_orm.Mapped[db_utils.TSVector] = sa_orm.mapped_column(
        db_utils.TSVector(),
        sa.Computed("to_tsvector('french', content)", persisted=True),
        nullable=False,
        name="__content_ts_vector__",
    )

    action_history: sa_orm.Mapped[list["ActionHistory"]] = sa_orm.relationship(
        "ActionHistory",
        foreign_keys="ActionHistory.chronicleId",
        back_populates="chronicle",
        order_by=ACTION_HISTORY_ORDER_BY,
        passive_deletes=True,
    )

    __table_args__ = (sa.Index("ix_chronicle_content___ts_vector__", _content_ts_vector, postgresql_using="gin"),)

    @hybrid_property
    def isPublished(self) -> bool:
        return self.isActive and self.isSocialMediaDiffusible

    @isPublished.inplace.expression
    @classmethod
    def _isPublishedExpression(cls) -> ColumnElement[bool]:
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
