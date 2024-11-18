import datetime
import logging
import typing

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql.elements import BinaryExpression

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from pcapi.core.users.models import User


class Chronicle(PcObject, Base, Model, DeactivableMixin):
    __tablename__ = "chronicle"
    age = sa.Column(sa.SmallInteger, nullable=True)
    city = sa.Column(sa.Text(), nullable=True)
    content = sa.Column(sa.Text, nullable=False)
    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ean = sa.Column(sa.Text(), nullable=True, index=True)
    # used to reconciliate data if the form changed on typeform
    eanChoiceId = sa.Column(sa.Text(), nullable=True)
    email = sa.Column(sa.Text(), nullable=False)
    firstName = sa.Column(sa.Text(), nullable=True)
    formId = sa.Column(sa.Text(), nullable=False)
    isIdentityDiffusible = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    isSocialMediaDiffusible: bool = sa.Column(
        sa.Boolean, nullable=False, server_default=sa.sql.expression.false(), default=False
    )
    products: list[sa_orm.Mapped["Product"]] = sa.orm.relationship(
        "Product", backref="chronicles", secondary="product_chronicle"
    )
    offers: sa_orm.Mapped["Offer"] = sa.orm.relationship("Offer", backref="chronicles", secondary="offer_chronicle")
    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    user: sa_orm.Mapped["User"] = sa.orm.relationship("User", foreign_keys=[userId], backref="chronicles")

    __content_ts_vector__ = db.Column(
        db_utils.TSVector(),
        db.Computed("to_tsvector('french', content)", persisted=True),
        nullable=False,
    )
    __table_args__ = (sa.Index("ix_chronicle_content___ts_vector__", __content_ts_vector__, postgresql_using="gin"),)

    @hybrid_property
    def isPublished(self) -> bool:
        return self.isActive and self.isSocialMediaDiffusible

    @isPublished.expression  # type: ignore[no-redef]
    def isPublished(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return sa.and_(cls.isActive.is_(True), cls.isSocialMediaDiffusible.is_(True))


ProductChronicle = sa.Table(
    "product_chronicle",
    Base.metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("productId", sa.ForeignKey(Product.id, ondelete="CASCADE"), index=True, nullable=False),
    sa.Column("chronicleId", sa.ForeignKey(Chronicle.id, ondelete="CASCADE"), index=True, nullable=False),
    sa.UniqueConstraint("productId", "chronicleId", name="unique_product_chronicle_constraint"),
)


OfferChronicle = sa.Table(
    "offer_chronicle",
    Base.metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("offerId", sa.ForeignKey(Offer.id, ondelete="CASCADE"), index=True, nullable=False),
    sa.Column("chronicleId", sa.ForeignKey(Chronicle.id, ondelete="CASCADE"), index=True, nullable=False),
    sa.UniqueConstraint("offerId", "chronicleId", name="unique_offer_chronicle_constraint"),
)
