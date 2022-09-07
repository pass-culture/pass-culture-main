import sqlalchemy as sqla

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class Criterion(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    name: str = sqla.Column(sqla.String(140), nullable=False, unique=True)
    description = sqla.Column(sqla.Text, nullable=True)
    startDateTime = sqla.Column(sqla.DateTime, nullable=True)
    endDateTime = sqla.Column(sqla.DateTime, nullable=True)

    def __str__(self) -> str:
        return self.name


class VenueCriterion(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    venueId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False
    )
    criterionId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("criterion.id", ondelete="CASCADE"), nullable=False, index=True
    )

    __table_args__ = (
        sqla.UniqueConstraint(
            "venueId",
            "criterionId",
            name="unique_venue_criterion",
        ),
    )


class OfferCriterion(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __table_name__ = "offer_criterion"
    offerId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    criterionId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("criterion.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        sqla.UniqueConstraint(
            "offerId",
            "criterionId",
            name="unique_offer_criterion",
        ),
    )
