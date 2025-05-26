import enum

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.users.models import User
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.pc_object import PcObject
from pcapi.utils.db import MagicEnum


class ReactionTypeEnum(enum.Enum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    NO_REACTION = "NO_REACTION"


class Reaction(PcObject, Base, Model):
    __tablename__ = "reaction"
    reactionType = sa.Column(MagicEnum(ReactionTypeEnum), nullable=False)
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", back_populates="reactions")
    offerId = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=True, index=True)
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", back_populates="reactions")
    productId = sa.Column(sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), nullable=True, index=True)
    product: sa_orm.Mapped["Product"] = sa_orm.relationship("Product", back_populates="reactions")

    __table_args__ = (
        # A reaction is linked to either an offer or a product
        # but not both at the same time
        sa.CheckConstraint(
            sa.or_(
                sa.and_(offerId.is_not(None), productId.is_(None)),
                sa.and_(productId.is_not(None), offerId.is_(None)),
            )
        ),
        sa.Index("reaction_offer_product_user_unique_constraint", "userId", "offerId", "productId", unique=True),
    )


@sa.event.listens_for(Reaction, "after_insert")
def after_insert_product_reaction(_mapper: sa_orm.Mapper, connection: sa.engine.Connection, target: Reaction) -> None:
    if target.productId and target.reactionType == ReactionTypeEnum.LIKE:
        _increment_product_counts(connection, target.productId, 1)


@sa.event.listens_for(Reaction.reactionType, "set")
def on_set_product_reaction(
    target: Reaction,
    value: ReactionTypeEnum,
    old_value: ReactionTypeEnum,
    _initiator: sa_orm.AttributeEvent,
) -> None:
    if target.productId is None:
        return

    if value == ReactionTypeEnum.LIKE and old_value != ReactionTypeEnum.LIKE:
        _increment_product_counts(db.session, target.productId, 1)
    elif value != ReactionTypeEnum.LIKE and old_value == ReactionTypeEnum.LIKE:
        _increment_product_counts(db.session, target.productId, -1)


@sa.event.listens_for(Reaction, "after_delete")
def after_delete_product_reaction(_mapper: sa_orm.Mapper, connection: sa.engine.Connection, target: Reaction) -> None:
    # SQLAlchemy will not call this event if the object is deleted using a bulk delete
    # (e.g. db.session.execute(sa.delete(Chronicle).where(...)))
    if target.productId and target.reactionType == ReactionTypeEnum.LIKE:
        _increment_product_counts(connection, target.productId, -1)


def _increment_product_counts(connection: sa.engine.Connection, product_id: int, increment: int) -> None:
    connection.execute(
        sa.update(Product).where(Product.id == product_id).values(likesCount=Product.likesCount + increment)
    )
