from datetime import datetime
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import SmallInteger

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class DepositType(enum.Enum):
    GRANT_15 = "GRANT_15"
    GRANT_16 = "GRANT_16"
    GRANT_17 = "GRANT_17"
    GRANT_18 = "GRANT_18"


class Deposit(PcObject, Model):
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    amount = Column(Numeric(10, 2), nullable=False)

    userId = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)

    user = relationship("User", foreign_keys=[userId], backref="deposits")

    source = Column(String(300), nullable=False)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    expirationDate = Column(DateTime, nullable=True)

    version = Column(SmallInteger, nullable=False)

    type = Column("type", Enum(DepositType, native_enum=False, create_constraint=False), nullable=False)
