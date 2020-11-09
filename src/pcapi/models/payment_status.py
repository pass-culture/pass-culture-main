from datetime import datetime
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class TransactionStatus(enum.Enum):
    PENDING = 'PENDING'
    NOT_PROCESSABLE = 'NOT PROCESSABLE'
    SENT = 'SENT'
    ERROR = 'ERROR'
    RETRY = 'RETRY'
    BANNED = 'BANNED'


class PaymentStatus(PcObject, Model):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    paymentId = Column(BigInteger,
                       ForeignKey("payment.id"),
                       index=True,
                       nullable=False)

    payment = relationship('Payment',
                           foreign_keys=[paymentId],
                           backref='statuses')

    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    status = Column(Enum(TransactionStatus), nullable=False)

    detail = Column(Text, nullable=True)
