""" user offerer """

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class UserSession(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    userId = Column(BigInteger, nullable=False)

    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
