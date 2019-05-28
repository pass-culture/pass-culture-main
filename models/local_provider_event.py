""" provider_event model """
import enum
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from models.pc_object import PcObject


class LocalProviderEventType(enum.Enum):
    SyncError = "SyncError"

    SyncPartStart = "SyncPartStart"
    SyncPartEnd = "SyncPartEnd"

    SyncStart = "SyncStart"
    SyncEnd = "SyncEnd"


class LocalProviderEvent(PcObject):

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    providerId = Column(BigInteger,
                        ForeignKey("provider.id"),
                        nullable=False)

    provider = relationship('Provider',
                            foreign_keys=[providerId])

    date = Column(DateTime,
                  nullable=False,
                  default=datetime.utcnow)

    type = Column(Enum(LocalProviderEventType),
                  nullable=False)

    payload = Column(String(50),
                     nullable=True)
