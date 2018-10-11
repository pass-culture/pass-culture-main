""" transfer model """

from sqlalchemy import BigInteger, \
    Column, \
    ForeignKey, \
    String, \
    Numeric, \
    Text
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

    amount = Column(Numeric(10, 2), nullable=False)

    reimbursementRule = Column(String(200), nullable=False)

    recipient = Column(String(140), nullable=False)

    iban = Column(String(27), nullable=True)

    comment = Column(Text, nullable=True)

    author = Column(String(27), nullable=False)
