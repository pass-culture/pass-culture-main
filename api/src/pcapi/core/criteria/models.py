import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class Criterion(PcObject, Model):  # type: ignore [valid-type, misc]
    name = sqla.Column(sqla.String(140), nullable=False, unique=True)
    description = sqla.Column(sqla.Text, nullable=True)
    startDateTime = sqla.Column(sqla.DateTime, nullable=True)
    endDateTime = sqla.Column(sqla.DateTime, nullable=True)

    def __str__(self) -> str:
        return self.name


class VenueCriterion(PcObject, Model):  # type: ignore [valid-type, misc]
    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False)
    venue = sqla_orm.relationship("Venue", foreign_keys=[venueId])  # type: ignore [misc]
    criterionId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("criterion.id", ondelete="CASCADE"), nullable=False, index=True
    )
    criterion = sqla_orm.relationship("Criterion", foreign_keys=[criterionId])

    __table_args__ = (
        sqla.UniqueConstraint(
            "venueId",
            "criterionId",
            name="unique_venue_criterion",
        ),
    )


class OfferCriterion(PcObject, Model):  # type: ignore [valid-type, misc]
    offerId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)
    offer = sqla_orm.relationship("Offer", foreign_keys=[offerId])  # type: ignore [misc]
    criterionId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("criterion.id", ondelete="CASCADE"), nullable=False)
    criterion = sqla_orm.relationship("Criterion", foreign_keys=[criterionId])

    __table_args__ = (
        sqla.UniqueConstraint(
            "offerId",
            "criterionId",
            name="unique_offer_criterion",
        ),
    )
