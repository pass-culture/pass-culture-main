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
                       nullable=False)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref='bank_information')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     index=True,
                     nullable=False)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         backref='bank_information')

    iban = Column(String(27),
                  nullable=False)

    bic = Column(String(11),
                 nullable=False)

    application_id = Column(Integer,
                            nullable=False)
