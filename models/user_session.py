""" user offerer """

from sqlalchemy import BigInteger, Column
from sqlalchemy.dialects.postgresql import UUID

from models.db import Model
from models.pc_object import PcObject


class UserSession(PcObject, Model):
    userId = Column(BigInteger, primary_key=True)

    uuid = Column(UUID(as_uuid=True), primary_key=True)
