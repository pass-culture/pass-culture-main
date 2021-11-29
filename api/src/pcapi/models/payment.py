""" transfer model """
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from pcapi.models import Model
from pcapi.models import db
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.models.pc_object import PcObject


class Payment(PcObject, Model):
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    bookingId = Column(BigInteger, ForeignKey("booking.id"), index=True, nullable=False)

    booking = relationship("Booking", foreign_keys=[bookingId], backref="payments")

    amount = Column(Numeric(10, 2), nullable=False)

    reimbursementRule = Column(String(200))

    reimbursementRate = Column(Numeric(10, 2))

    customReimbursementRuleId = Column(
        BigInteger,
        ForeignKey("custom_reimbursement_rule.id"),
    )

    customReimbursementRule = relationship(
        "CustomReimbursementRule", foreign_keys=[customReimbursementRuleId], backref="payments"
    )

    recipientName = Column(String(140), nullable=False)

    recipientSiren = Column(String(9), nullable=False)

    iban = Column(String(27), nullable=True)

    bic = Column(
        String(11),
        CheckConstraint(
            "(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)",
            name="check_iban_and_bic_xor_not_iban_and_not_bic",
        ),
        nullable=True,
    )

    comment = Column(Text, nullable=True)

    author = Column(String(27), nullable=False)

    transactionEndToEndId = Column(UUID(as_uuid=True), nullable=True)

    transactionLabel = Column(String(140), nullable=True)

    paymentMessageId = Column(BigInteger, ForeignKey("payment_message.id"), nullable=True)

    paymentMessage = relationship("PaymentMessage", foreign_keys=[paymentMessageId], backref=backref("payments"))

    batchDate = Column(DateTime, nullable=True, index=True)

    __table_args__ = (
        CheckConstraint(
            """
            (
              "reimbursementRule" IS NOT NULL
              AND "reimbursementRate" IS NOT NULL
              AND "customReimbursementRuleId" IS NULL
            ) OR (
              "reimbursementRule" IS NULL
              AND "customReimbursementRuleId" IS NOT NULL
            )
            """,
            name="reimbursement_constraint_check",
        ),
    )

    @property
    def paymentMessageName(self):
        return self.paymentMessage.name if self.paymentMessage else None

    @property
    def paymentMessageChecksum(self):
        return self.paymentMessage.checksum if self.paymentMessage else None

    @hybrid_property
    def currentStatus(self):
        statuses_by_date_desc = sorted(self.statuses, key=lambda x: x.date, reverse=True)
        return statuses_by_date_desc[0]

    @currentStatus.expression
    def currentStatus(cls):  # pylint: disable=no-self-argument
        return (
            db.session.query(PaymentStatus.status)
            .filter(PaymentStatus.paymentId == cls.id)
            .order_by(desc(PaymentStatus.date))
            .limit(1)
            .as_scalar()
        )

    @hybrid_property
    def lastProcessedDate(self):
        payment_sent_date = [status.date for status in self.statuses if status.status == TransactionStatus.SENT]
        sorted_sent_dates = sorted(payment_sent_date, key=lambda x: x.date)
        return sorted_sent_dates[0] if len(sorted_sent_dates) > 0 else None

    @lastProcessedDate.expression
    def lastProcessedDate(cls):  # pylint: disable=no-self-argument
        return (
            db.session.query(PaymentStatus.date)
            .filter(PaymentStatus.paymentId == cls.id)
            .filter(PaymentStatus.status == TransactionStatus.SENT)
            .order_by(PaymentStatus.date.asc())
            .limit(1)
            .as_scalar()
        )

    def setStatus(self, status: TransactionStatus, detail: str = None):
        payment_status = PaymentStatus()
        payment_status.status = status
        payment_status.date = datetime.utcnow()
        payment_status.detail = detail

        self.statuses.append(payment_status)
