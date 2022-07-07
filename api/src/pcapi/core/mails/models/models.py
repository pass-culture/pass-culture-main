import dataclasses
from datetime import datetime
import enum

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import JSONB

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


@dataclasses.dataclass
class MailResult:
    sent_data: dict
    successful: bool


class EmailStatus(enum.Enum):
    SENT = "SENT"
    ERROR = "ERROR"


class Email(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    content = Column("content", JSONB, nullable=False)
    status = Column(Enum(EmailStatus), nullable=False, index=True)

    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
