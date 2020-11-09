""" transfer model """

from sqlalchemy import Column
from sqlalchemy import LargeBinary
from sqlalchemy import String

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class PaymentMessage(PcObject, Model):
    name = Column(String(50), unique=True, nullable=False)

    checksum = Column(LargeBinary(32), unique=True, nullable=False)
