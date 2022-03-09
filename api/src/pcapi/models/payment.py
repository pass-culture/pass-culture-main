""" transfer model """

from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from pcapi.models import Model
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
