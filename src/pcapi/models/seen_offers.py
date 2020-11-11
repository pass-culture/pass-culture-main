from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from pcapi.models import PcObject
from pcapi.models.db import Model


class SeenOffer(PcObject, Model):
    dateSeen = Column(DateTime, nullable=False)
    offerId = Column(BigInteger, ForeignKey("offer.id"), nullable=False, index=True)
    userId = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    offer = relationship("Offer", foreign_keys=[offerId], backref="SeenOffer")
    user = relationship("UserSQLEntity", foreign_keys=[userId], backref="SeenOffer")
