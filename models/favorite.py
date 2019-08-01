from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from models.pc_object import PcObject
from models.db import Model


class Favorite(PcObject, Model):
    userId = Column(BigInteger,
                    ForeignKey("user.id"),
                    index=True,
                    nullable=False)

    user = relationship('User',
                        foreign_keys=[userId])

    offerId = Column(BigInteger,
                     ForeignKey("offer.id"),
                     index=True,
                     nullable=False)

    offer = relationship('Offer',
                         foreign_keys=[offerId],
                         backref='favorites')

    mediationId = Column(BigInteger,
                         ForeignKey("mediation.id"),
                         index=True,
                         nullable=True)

    mediation = relationship('Mediation',
                             foreign_keys=[mediationId],
                             backref='favorites')

    @property
    def thumbUrl(self):
        if self.mediationId:
            return self.mediation.thumbUrl

        if self.offer.product.thumbCount:
            return self.offer.product.thumbUrl
