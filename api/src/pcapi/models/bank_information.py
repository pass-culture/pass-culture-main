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

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class BankInformationStatus(enum.Enum):
    REJECTED = "REJECTED"
    DRAFT = "DRAFT"
    ACCEPTED = "ACCEPTED"


class BankInformation(PcObject, Model):  # type: ignore [valid-type, misc]
    offererId = Column(BigInteger, ForeignKey("offerer.id"), index=True, nullable=True, unique=True)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref=backref("bankInformation", uselist=False))  # type: ignore [misc]

    venueId = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=True, unique=True)

    venue = relationship("Venue", foreign_keys=[venueId], backref=backref("bankInformation", uselist=False))  # type: ignore [misc]

    iban = Column(String(27), nullable=True)

    bic = Column(String(11), nullable=True)

    applicationId = Column(Integer, nullable=True, index=True, unique=True)

    status = Column(Enum(BankInformationStatus), nullable=False)

    dateModified = Column(DateTime, nullable=True)
