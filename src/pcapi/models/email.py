from datetime import datetime
import enum

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import JSON

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class EmailStatus(enum.Enum):
    SENT = 'SENT'
    ERROR = 'ERROR'


class Email(PcObject, Model):
    content = Column(JSON,
                     nullable=False)
    status = Column(Enum(EmailStatus),
                    nullable=False,
                    index=True)

    datetime = Column(DateTime,
                      nullable=False,
                      default=datetime.utcnow)
