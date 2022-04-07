from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class Criterion(PcObject, Model):  # type: ignore [valid-type, misc]
    name = Column(String(140), nullable=False, unique=True)

    description = Column(Text, nullable=True)

    startDateTime = Column(DateTime, nullable=True)

    endDateTime = Column(DateTime, nullable=True)

    def __repr__(self):  # type: ignore [no-untyped-def]
        return "%s" % self.name
