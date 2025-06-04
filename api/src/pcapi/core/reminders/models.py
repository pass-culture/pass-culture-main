import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.offers.models import FutureOffer
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class FutureOfferReminder(PcObject, Base, Model):
    __tablename__ = "future_offer_reminder"

    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", backref="future_offer_reminders")
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    futureOffer: sa_orm.Mapped["FutureOffer"] = sa_orm.relationship("FutureOffer", backref="future_offer_reminders")
    futureOfferId: int = sa.Column(sa.BigInteger, sa.ForeignKey("future_offer.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "futureOfferId",
            name="unique_reminder_per_user_per_future_offer",
        ),
    )


class OfferReminder(PcObject, Base, Model):
    __tablename__ = "offer_reminder"

    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", backref="offer_reminders")
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", backref="offer_reminders")
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "offerId",
            name="unique_user_offer_reminder",
        ),
    )
