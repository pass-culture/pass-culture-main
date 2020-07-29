from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from models.db import Model
from models.pc_object import PcObject


class OfferCriterion(PcObject, Model):
    offerId = Column(BigInteger,
                     ForeignKey('offer.id'),
                     index=True,
                     nullable=False)

    offer = relationship('OfferSQLEntity',
                         foreign_keys=[offerId],
                         backref='offerCriteria')

    criterionId = Column(BigInteger,
                         ForeignKey('criterion.id'),
                         nullable=False)

    criterion = relationship('Criterion',
                             foreign_keys=[criterionId],
                             backref='offerCriteria')
