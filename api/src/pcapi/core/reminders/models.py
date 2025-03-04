import sqlalchemy as sa

from pcapi.core.offers.models import FutureOffer
from pcapi.core.users.models import User
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class FutureOfferReminder(PcObject, Base, Model):
    __tablename__ = "future_offer_reminder"

    user: sa.orm.Mapped["User"] = sa.orm.relationship("User", backref="future_offer_reminders")
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    futureOffer: sa.orm.Mapped["FutureOffer"] = sa.orm.relationship("FutureOffer", backref="future_offer_reminders")
    futureOfferId: int = sa.Column(sa.BigInteger, sa.ForeignKey("future_offer.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "futureOfferId",
            name="unique_reminder_per_user_per_future_offer",
        ),
    )
