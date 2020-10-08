""" user offerer """

from sqlalchemy import BigInteger, Column
from sqlalchemy.dialects.postgresql import UUID

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class UserSession(PcObject, Model):
    userId = Column(BigInteger, nullable=False)

    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
