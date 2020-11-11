""" api key model """

from sqlalchemy import BigInteger
from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class ApiKey(PcObject, Model):
    value = Column(CHAR(64), index=True, nullable=False)

    offererId = Column(BigInteger, ForeignKey("offerer.id"), index=True, nullable=False)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref=backref("apiKey", uselist=False))
