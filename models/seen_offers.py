from sqlalchemy import BigInteger, ForeignKey, Column, DateTime
from sqlalchemy.orm import relationship

from models import PcObject
from models.db import Model


class SeenOffer(PcObject, Model):
    dateSeen = Column(DateTime, nullable=False)
    offerId = Column(BigInteger, ForeignKey('offer.id'), nullable=False, index=True)
    userId = Column(BigInteger, ForeignKey('user.id'), nullable=False, index=True)
    offer = relationship('OfferSQLEntity',
                         foreign_keys=[offerId],
                         backref='SeenOffer')
    user = relationship('UserSQLEntity',
                        foreign_keys=[userId],
                        backref='SeenOffer')
