""" transfer model """

from sqlalchemy import Column, \
    String

from models.db import Model
from models.pc_object import PcObject


class PaymentTransaction(PcObject, Model):
    messageId = Column(String(50), unique=True, nullable=False)

    checksum = Column(String(40), unique=True, nullable=False)
