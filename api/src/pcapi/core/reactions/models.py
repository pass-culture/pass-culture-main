import enum
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.db import MagicEnum


if TYPE_CHECKING:
    from pcapi.core.offers.models import Offer
    from pcapi.core.offers.models import Product
    from pcapi.core.users.models import User


class ReactionTypeEnum(enum.Enum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    NO_REACTION = "NO_REACTION"


class Reaction(PcObject, Base, Model):
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
