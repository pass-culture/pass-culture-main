from datetime import datetime
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject
from pcapi.models.versioned_mixin import VersionedMixin


class BankInformationStatus(enum.Enum):
    REJECTED = "REJECTED"
    DRAFT = "DRAFT"
    ACCEPTED = "ACCEPTED"


class BankInformation(PcObject, Model, VersionedMixin):
    offererId = Column(BigInteger,
                       ForeignKey("offerer.id"),
                       index=True,
                       nullable=True,
                       unique=True)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref=backref('bankInformation', uselist=False))

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     index=True,
                     nullable=True,
                     unique=True)

    venue = relationship('VenueSQLEntity',
                         foreign_keys=[venueId],
                         backref=backref('bankInformation', uselist=False))

    iban = Column(String(27),
                  nullable=True)

    bic = Column(String(11),
                 nullable=True)

    applicationId = Column(Integer,
                           nullable=False,
                           unique=True)

    status = Column(Enum(BankInformationStatus), nullable=False)

    dateModified = Column(DateTime,
                          nullable=True,
                          default=datetime.utcnow)
