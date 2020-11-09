from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class IrisVenues(PcObject, Model):
    irisId = Column(BigInteger, ForeignKey('iris_france.id'), nullable=False, index=True)
    venueId = Column(BigInteger, ForeignKey('venue.id'), nullable=False)
    venue = relationship('VenueSQLEntity',
                         foreign_keys=[venueId],
                         backref='IrisVenues')
    iris = relationship('IrisFrance',
                        foreign_keys=[irisId],
                        backref='IrisVenues')
