from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from models.pc_object import PcObject
from models.db import Model


class IrisVenues(PcObject, Model):
    irisId = Column(BigInteger, ForeignKey('iris_france.id'), nullable=False)
    venueId = Column(BigInteger, ForeignKey('venue.id'), nullable=False)
    venue = relationship('VenueSQLEntity',
                         foreign_keys=[venueId],
                         backref='IrisVenues')
    iris = relationship('IrisFrance',
                        foreign_keys=[irisId],
                        backref='IrisVenues')
