from sqlalchemy import Column, BigInteger, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from models.db import Model
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class BankInformation(PcObject,
                      Model,
                      ProvidableMixin):
    offererId = Column(BigInteger,
                       ForeignKey("offerer.id"),
                       index=True,
                       nullable=True)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           uselist=False,
                           backref='bankInformation')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     index=True,
                     nullable=True)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         uselist=False,
                         backref='bankInformation')

    iban = Column(String(27),
                  nullable=False)

    bic = Column(String(11),
                 nullable=False)

    applicationId = Column(Integer,
                           nullable=False)
