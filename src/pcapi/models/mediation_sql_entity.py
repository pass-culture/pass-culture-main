from datetime import datetime

from sqlalchemy import Column, \
    BigInteger, \
    DateTime, \
    ForeignKey, \
    String
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin


class MediationSQLEntity(PcObject,
                         Model,
                         HasThumbMixin,
                         ProvidableMixin,
                         DeactivableMixin):
    __tablename__ = 'mediation'

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    credit = Column(String(255), nullable=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    authorId = Column(BigInteger,
                      ForeignKey("user.id"),
                      nullable=True)

    author = relationship('UserSQLEntity',
                          foreign_keys=[authorId],
                          backref='mediations')

    offerId = Column(BigInteger,
                     ForeignKey('offer.id'),
                     index=True,
                     nullable=False)

    offer = relationship('Offer',
                         foreign_keys=[offerId],
                         backref='mediations')
