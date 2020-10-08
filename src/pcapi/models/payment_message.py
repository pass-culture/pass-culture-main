""" transfer model """

from sqlalchemy import Column, \
    String, Binary

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class PaymentMessage(PcObject, Model):
    name = Column(String(50), unique=True, nullable=False)

    checksum = Column(Binary(32), unique=True, nullable=False)
