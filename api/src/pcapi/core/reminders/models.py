import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class OfferReminder(PcObject, Model):
    __tablename__ = "offer_reminder"

    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", foreign_keys=[userId], back_populates="offer_reminders")
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship(
        "Offer", foreign_keys=[offerId], back_populates="offer_reminders"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "offerId",
            name="unique_user_offer_reminder",
        ),
    )
