from datetime import datetime
import decimal
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import Numeric

from pcapi.core.educational import exceptions
from pcapi.models.db import Model


class EducationalBookingStatus(enum.Enum):
    REFUSED = "REFUSED"
    USED_BY_INSTITUTE = "USED_BY_INSTITUTE"


class EducationalInstitution(Model):
    __tablename__ = "educational_institution"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    institutionId = Column(String(30), nullable=False, unique=True, index=True)


class EducationalYear(Model):
    __tablename__ = "educational_year"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    adageId = Column(String(30), unique=True, nullable=False)

    beginningDate = Column(DateTime, nullable=False)

    expirationDate = Column(DateTime, nullable=False)


class EducationalDeposit(Model):
    __tablename__ = "educational_deposit"

    TEMPORARY_FUND_AVAILABLE_RATIO = 0.8

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    educationalInstitutionId = Column(BigInteger, ForeignKey("educational_institution.id"), index=True, nullable=False)

    educationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="deposits"
    )

    educationalYearId = Column(String(30), ForeignKey("educational_year.adageId"), index=True, nullable=False)

    educationalYear = relationship(EducationalYear, foreign_keys=[educationalYearId], backref="deposits")

    amount = Column(Numeric(10, 2), nullable=False)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    isFinal = Column(Boolean, nullable=False, default=True)

    def get_amount(self) -> decimal.Decimal:
        return (
            round(self.amount * decimal.Decimal(self.TEMPORARY_FUND_AVAILABLE_RATIO), 2)
            if not self.isFinal
            else self.amount
        )

    def check_has_enough_fund(self, total_amount_after_booking: decimal.Decimal) -> None:
        if self.amount < total_amount_after_booking:
            raise exceptions.InsufficientFund()

        if self.get_amount() < total_amount_after_booking and not self.isFinal:
            raise exceptions.InsufficientTemporaryFund()

        return


class EducationalBooking(Model):
    __tablename__ = "educational_booking"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    educationalInstitutionId = Column(BigInteger, ForeignKey("educational_institution.id"), nullable=False)
    educationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="educationalBookings"
    )

    educationalYearId = Column(BigInteger, ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear = relationship(EducationalYear, foreign_keys=[educationalYearId])

    Index("ix_educational_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    status = Column(
        "status",
        Enum(EducationalBookingStatus),
        nullable=True,
    )

    confirmationDate = Column(DateTime, nullable=True)
    confirmationLimitDate = Column(DateTime, nullable=True)
