from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class OfferCriterion(PcObject, Model):  # type: ignore [valid-type, misc]
    offerId = Column(BigInteger, ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)

    offer = relationship("Offer", foreign_keys=[offerId])  # type: ignore [misc]

    criterionId = Column(BigInteger, ForeignKey("criterion.id", ondelete="CASCADE"), nullable=False)

    criterion = relationship("Criterion", foreign_keys=[criterionId])  # type: ignore [misc]

    __table_args__ = (
        UniqueConstraint(
            "offerId",
            "criterionId",
            name="unique_offer_criterion",
        ),
    )
