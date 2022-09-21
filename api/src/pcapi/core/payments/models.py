from dataclasses import dataclass
import datetime
from decimal import Decimal
import enum

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import SmallInteger

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class DepositType(enum.Enum):
    GRANT_15_17 = "GRANT_15_17"
    GRANT_18 = "GRANT_18"


class Deposit(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    amount: Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    user = relationship("User", foreign_keys=[userId], backref="deposits")  # type: ignore [misc]

    individual_bookings = relationship("IndividualBooking", back_populates="deposit")  # type: ignore [misc]

    source: str = sa.Column(sa.String(300), nullable=False)

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    dateUpdated = sa.Column(sa.DateTime, nullable=True, onupdate=sa.func.now())

    expirationDate = sa.Column(sa.DateTime, nullable=True)

    version: int = sa.Column(SmallInteger, nullable=False)

    type: DepositType = sa.Column(
        sa.Enum(DepositType, native_enum=False, create_constraint=False),
        nullable=False,
        server_default=DepositType.GRANT_18.value,
    )

    recredits = relationship("Recredit", order_by="Recredit.dateCreated.desc()", back_populates="deposit")  # type: ignore [misc]

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "type",
            name="unique_type_per_user",
        ),
    )

    @property
    def specific_caps(self):  # type: ignore [no-untyped-def]
        from . import conf

        return conf.SPECIFIC_CAPS[self.type][self.version]


@dataclass
class GrantedDeposit:
    amount: Decimal
    expiration_date: datetime.datetime
    type: DepositType
    version: int = 1


class RecreditType(enum.Enum):
    RECREDIT_16 = "Recredit16"
    RECREDIT_17 = "Recredit17"
    MANUAL_MODIFICATION = "ManualModification"


class Recredit(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    depositId: int = sa.Column(sa.BigInteger, sa.ForeignKey("deposit.id"), nullable=False)

    deposit = relationship("Deposit", foreign_keys=[depositId], back_populates="recredits")  # type: ignore [misc]

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    amount: Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)

    recreditType: RecreditType = sa.Column(
        sa.Enum(RecreditType, native_enum=False, create_constraint=False),
        nullable=False,
    )

    comment = sa.Column(sa.Text, nullable=True)
