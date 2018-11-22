""" transfer model """
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, \
    Column, \
    ForeignKey, \
    String, \
    Numeric, \
    Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
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

    recipientName = Column(String(140), nullable=False)

    recipientSiren = Column(String(9), nullable=False)

    iban = Column(String(27), nullable=True)

    bic = Column(String(11),
                 CheckConstraint('(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)',
                                 name='check_iban_and_bic_xor_not_iban_and_not_bic'),
                 nullable=True)

    comment = Column(Text, nullable=True)

    author = Column(String(27), nullable=False)

    transactionMessageId = Column(String(50), nullable=True)

    transactionEndToEndId = Column(UUID(as_uuid=True), nullable=True)

    def setStatus(self, status: TransactionStatus, detail: str=None):
        payment_status = PaymentStatus()
        payment_status.status = status
        payment_status.date = datetime.utcnow()
        payment_status.detail = detail

        if self.statuses:
            self.statuses.append(payment_status)
        else:
            self.statuses = [payment_status]

    def setTransactionIds(self, message_id: str, end_to_end_id: uuid.UUID):
        self.transactionMessageId = message_id
        self.transactionEndToEndId = end_to_end_id

    def nullifyTransactionIds(self):
        self.transactionMessageId = None
        self.transactionEndToEndId = None