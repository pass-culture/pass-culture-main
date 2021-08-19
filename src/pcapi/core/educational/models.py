from datetime import datetime
from decimal import Decimal
import enum
from typing import Optional

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

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.educational import exceptions
from pcapi.models.db import Model


class EducationalBookingStatus(enum.Enum):
    REFUSED = "REFUSED"
    USED_BY_INSTITUTE = "USED_BY_INSTITUTE"


class EducationalInstitution(Model):
    __tablename__ = "educational_institution"

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)

    institutionId: str = Column(String(30), nullable=False, unique=True, index=True)


class EducationalYear(Model):
    __tablename__ = "educational_year"

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)

    adageId: str = Column(String(30), unique=True, nullable=False)

    beginningDate: datetime = Column(DateTime, nullable=False)

    expirationDate: datetime = Column(DateTime, nullable=False)


class EducationalDeposit(Model):
    __tablename__ = "educational_deposit"

    TEMPORARY_FUND_AVAILABLE_RATIO = 0.8

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)

    educationalInstitutionId = Column(BigInteger, ForeignKey("educational_institution.id"), index=True, nullable=False)

    educationalInstitution: EducationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="deposits"
    )

    educationalYearId = Column(String(30), ForeignKey("educational_year.adageId"), index=True, nullable=False)

    educationalYear: EducationalYear = relationship(
        EducationalYear, foreign_keys=[educationalYearId], backref="deposits"
    )

    amount: Decimal = Column(Numeric(10, 2), nullable=False)

    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    isFinal: bool = Column(Boolean, nullable=False, default=True)

    def get_amount(self) -> Decimal:
        return round(self.amount * Decimal(self.TEMPORARY_FUND_AVAILABLE_RATIO), 2) if not self.isFinal else self.amount

    def check_has_enough_fund(self, total_amount_after_booking: Decimal) -> None:
        if self.amount < total_amount_after_booking:
            raise exceptions.InsufficientFund()

        if self.get_amount() < total_amount_after_booking and not self.isFinal:
            raise exceptions.InsufficientTemporaryFund()

        return


class EducationalRedactor(Model):

    __tablename__ = "educational_redactor"

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)

    email: str = Column(String(120), nullable=False, unique=True, index=True)

    firstName: str = Column(String(128), nullable=False)

    lastName: str = Column(String(128), nullable=False)

    civility: str = Column(String(20), nullable=False)

    educationalBookings = relationship(
        "EducationalBooking",
        back_populates="educationalRedactor",
    )


class EducationalBooking(Model):
    __tablename__ = "educational_booking"

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)

    educationalInstitutionId = Column(BigInteger, ForeignKey("educational_institution.id"), nullable=False)
    educationalInstitution: EducationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="educationalBookings"
    )

    educationalYearId = Column(String(30), ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear: EducationalYear = relationship(EducationalYear, foreign_keys=[educationalYearId])

    Index("ix_educational_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    status = Column(
        "status",
        Enum(EducationalBookingStatus),
        nullable=True,
    )

    confirmationDate: Optional[datetime] = Column(DateTime, nullable=True)
    confirmationLimitDate = Column(DateTime, nullable=True)

    booking = relationship(
        "Booking",
        back_populates="educationalBooking",
        uselist=False,
        lazy="joined",
        innerjoin=True,
    )

    educationalRedactorId = Column(
        BigInteger,
        ForeignKey("educational_redactor.id"),
        nullable=True,
        index=True,
    )
    educationalRedactor: EducationalRedactor = relationship(
        EducationalRedactor,
        back_populates="educationalBookings",
        uselist=False,
    )

    def mark_as_used_by_institute(self) -> None:
        from pcapi.core.bookings.models import BookingStatus

        if self.booking.status != BookingStatus.CONFIRMED:
            raise exceptions.EducationalBookingNotConfirmedYet()

        self.status = EducationalBookingStatus.USED_BY_INSTITUTE

    def mark_as_refused(self) -> None:
        from pcapi.core.bookings.models import BookingCancellationReasons

        if self.status == EducationalBookingStatus.USED_BY_INSTITUTE:
            raise exceptions.EducationalBookingNotRefusable()

        try:
            self.booking.cancel_booking()
            self.booking.cancellationReason = BookingCancellationReasons.REFUSED_BY_INSTITUTE
        except booking_exceptions.BookingIsAlreadyUsed:
            raise exceptions.EducationalBookingNotRefusable()
        except booking_exceptions.BookingIsAlreadyCancelled:
            raise exceptions.EducationalBookingAlreadyCancelled()

        self.status = EducationalBookingStatus.REFUSED
