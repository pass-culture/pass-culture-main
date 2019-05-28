""" transfer model """

from sqlalchemy import Column, \
    String, Binary

from models.pc_object import PcObject


class PaymentMessage(PcObject):
    name = Column(String(50), unique=True, nullable=False)

    checksum = Column(Binary(32), unique=True, nullable=False)
