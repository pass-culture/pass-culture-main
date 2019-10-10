""" api key model """

from sqlalchemy import BigInteger, Column, CHAR, ForeignKey


from models.db import Model
from models.pc_object import PcObject

from sqlalchemy.orm import relationship, backref


class ApiKey(PcObject, Model):
    # child
    value = Column(CHAR(64),
                   index=True,
                   nullable=False
                   )

    offererId = Column(BigInteger,
                       ForeignKey('offerer.id'),
                       index=True,
                       nullable=False)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref=backref('apiKey', uselist=False))