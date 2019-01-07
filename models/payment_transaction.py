""" transfer model """

from sqlalchemy import Column, \
    String, Binary

from models.db import Model
from models.pc_object import PcObject


class PaymentTransaction(PcObject, Model):
    messageId = Column(String(50), unique=True, nullable=False)

    checksum = Column(Binary(32), unique=True, nullable=False)
