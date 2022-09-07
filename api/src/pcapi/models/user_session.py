""" user offerer """

from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy.dialects import postgresql

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class UserSession(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    userId: int = Column(BigInteger, nullable=False)

    uuid: UUID = Column(postgresql.UUID(as_uuid=True), unique=True, nullable=False)
