""" transfer model """
from datetime import datetime

from sqlalchemy import BigInteger, \
    Column, \
    ForeignKey, \
    String, \
    Numeric, \
    Text, CheckConstraint
from sqlalchemy.orm import relationship

from models.db import Model
from models.payment_status import TransactionStatus, PaymentStatus
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

    bic = Column(String(11),
                 CheckConstraint('(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)',
                                 name='check_iban_and_bic_xor_not_iban_and_not_bic'),
                 nullable=True)

    comment = Column(Text, nullable=True)

    author = Column(String(27), nullable=False)

    transactionMessageId = Column(String(50), nullable=True)

    transactionPaymentInfoId = Column(String(50), nullable=True)

    def setStatus(self, status: TransactionStatus, detail: str=None):
        payment_status = PaymentStatus()
        payment_status.status = status
        payment_status.date = datetime.utcnow()
        payment_status.detail = detail

        if self.statuses:
            self.statuses.append(payment_status)
        else:
            self.statuses = [payment_status]
