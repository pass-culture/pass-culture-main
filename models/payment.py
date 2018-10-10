""" transfer model """
import enum

from sqlalchemy import BigInteger, \
    Column, \
    ForeignKey, \
    String, \
    Numeric, \
    Text, \
    Enum
from sqlalchemy.orm import relationship

from models.db import Model
from models.pc_object import PcObject


class Payment(PcObject, Model):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    bookingId = Column(BigInteger,
                       ForeignKey("booking.id"),
                       index=True,
                       nullable=False)

    booking = relationship('Booking',
                           foreign_keys=[bookingId],
                           backref='payments')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     index=True,
                     nullable=False)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         backref='payments')

    amount = Column(Numeric(10, 2), nullable=False)

    iban = Column(String(27), nullable=True)

    comment = Column(Text, nullable=True)

    author = Column(String(27), nullable=False)
