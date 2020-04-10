from sqlalchemy import BigInteger, ForeignKey, Column, DateTime
from sqlalchemy.orm import relationship

from models import PcObject
from models.db import Model


class SeenOffers(PcObject, Model):
    dateSeen = Column(DateTime, nullable=False)
    offerId = Column(BigInteger, ForeignKey('offer.id'), nullable=False, index=True)
    userId = Column(BigInteger, ForeignKey('user.id'), nullable=False, index=True)
    offer = relationship('Offer',
                         foreign_keys=[offerId],
                         backref='SeenOffers')
    user = relationship('User',
                        foreign_keys=[userId],
                        backref='SeenOffers')
