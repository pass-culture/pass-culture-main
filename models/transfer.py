""" transfer model """
from datetime import datetime
from enum import Enum
from sqlalchemy import BigInteger, \
    Boolean, \
    Column, \
    DateTime, \
    DDL, \
    event, \
    ForeignKey, \
    Integer, \
    String, Numeric
from sqlalchemy.orm import relationship

from models.db import Model
from models.pc_object import PcObject


class TransferStatus(Enum):
    PENDING = 'PENDING'
    ERROR = 'ERROR'
    DONE = 'DONE'


class TransferType(Enum):
    INITIAL = 'INITIAL'
    CORRECTION = 'CORRECTION'


class Transfer(PcObject,
               Model):

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    bookingId = Column(BigInteger,
                       ForeignKey("booking.id"),
                       index=True,
                       nullable=False)

    booking = relationship('Booking',
                           foreign_keys=[bookingId],
                           backref='transfers')

    offererId = Column(BigInteger,
                       ForeignKey("offerer.id"),
                       index=True,
                       nullable=False)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref='transfers')

    amount = Column(Numeric(10, 2),
                    nullable=False)

    type = Column(Enum(TransferType),
                  nullable=False)

    iban = Column(String(27),
                  nullable=True)

    status = Column(Enum(TransferStatus),
                    nullable=False)
