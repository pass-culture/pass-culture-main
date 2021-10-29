from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class OfferCriterion(PcObject, Model):
    offerId = Column(BigInteger, ForeignKey("offer.id"), index=True, nullable=False)

    offer = relationship("Offer", foreign_keys=[offerId])

    criterionId = Column(BigInteger, ForeignKey("criterion.id"), nullable=False)

    criterion = relationship("Criterion", foreign_keys=[criterionId])
