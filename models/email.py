import enum
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, JSON

from models.db import Model
from models.pc_object import PcObject


class EmailStatus(enum.Enum):
    SENT = 'SENT'
    ERROR = 'ERROR'


class Email(PcObject,
            Model,
            ):
    content = Column(JSON,
                     nullable=False)
    status = Column(Enum(EmailStatus),
                    nullable=False,
                    index=True)

    datetime = Column(DateTime,
                      nullable=False,
                      default=datetime.utcnow)
