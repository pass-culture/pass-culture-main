import dataclasses
from datetime import datetime
import enum

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


@dataclasses.dataclass
class MailResult:
    sent_data: dict
    successful: bool


class EmailStatus(enum.Enum):
    SENT = "SENT"
    ERROR = "ERROR"


class Email(PcObject, Model):
    _content = Column("content", JSON, nullable=False)
    _contentNew = Column("contentNew", JSONB)  # TODO (ASK, JSONB): set this none nullable when JSONB migration is done
    status = Column(Enum(EmailStatus), nullable=False, index=True)

    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    @hybrid_property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        self._contentNew = value
