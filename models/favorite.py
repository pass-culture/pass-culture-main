from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from models.db import Model
from models.pc_object import PcObject


class Favorite(PcObject, Model):
    userId = Column(BigInteger,
                    ForeignKey("user.id"),
                    index=True,
                    nullable=False)

    user = relationship('UserSQLEntity',
                        foreign_keys=[userId],
                        backref='favorites')

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

    __table_args__ = (
        UniqueConstraint(
            'userId',
            'offerId',
            name='unique_favorite',
        ),
    )

    @property
    def thumbUrl(self):
        if self.mediationId:
            return self.mediation.thumbUrl
        return self.offer.product.thumbUrl
