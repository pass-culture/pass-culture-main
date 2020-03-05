from sqlalchemy import Column, BigInteger

from models.pc_object import PcObject
from models.db import Model


class IrisVenues(PcObject, Model):
    irisId = Column(BigInteger, nullable=False)
    venueId = Column(BigInteger, nullable=False)