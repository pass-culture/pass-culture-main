import enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


ALGORITHM_HS_256 = "HS256"


class TokenType(enum.Enum):
    RESET_PASSWORD = "reset-password"


class Token(PcObject, Model):
    __tablename__ = "token"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    userId = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)

    user = relationship("UserSQLEntity", foreign_keys=[userId], backref="tokens")

    value = Column(String, index=True, unique=True, nullable=False)

    type = Column(Enum(TokenType, create_constraint=False), nullable=False)

    creationDate = Column(DateTime, nullable=False, server_default=func.now())

    expirationDate = Column(DateTime, nullable=True)
