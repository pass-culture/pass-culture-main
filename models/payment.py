""" transfer model """
from datetime import datetime
import enum
from sqlalchemy import BigInteger, \
    Boolean, \
    Column, \
    DateTime, \
    DDL, \
    event, \
    ForeignKey, \
    Integer, \
    String,\
    Numeric,\
    Text, \
    Enum
from sqlalchemy.orm import relationship

from models.db import Model
from models.pc_object import PcObject


class PaymentStatus(enum.Enum):
    PENDING = 'PENDING'
    ERROR = 'ERROR'
    DONE = 'DONE'


class PaymentType(enum.Enum):
    INITIAL = 'INITIAL'
    CORRECTION = 'CORRECTION'


class Payment(PcObject,
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
                           backref='payments')

    offererId = Column(BigInteger,
                       ForeignKey("offerer.id"),
                       index=True,
                       nullable=False)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref='payments')

    amount = Column(Numeric(10, 2),
                    nullable=False)

    type = Column(Enum(PaymentType),
                  nullable=False)

    iban = Column(String(27),
                  nullable=True)

    status = Column(Enum(PaymentStatus),
                    nullable=False)

    dateStatus = Column(DateTime,
                        nullable=False)

    comment = Column(Text,
                     nullable=True)

    author = Column(String(27),
                    nullable=False)

