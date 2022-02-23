import dataclasses
from datetime import datetime
from decimal import Decimal
import enum
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.sqltypes import Numeric

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.educational import exceptions
from pcapi.models import Model
from pcapi.models.offer_mixin import AccessibilityMixin
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import StatusMixin
from pcapi.models.offer_mixin import ValidationMixin
from pcapi.models.pc_object import PcObject


class StudentLevels(enum.Enum):
    COLLEGE4 = "Collège - 4e"
    COLLEGE3 = "Collège - 3e"
    CAP1 = "CAP - 1re année"
    CAP2 = "CAP - 2e année"
    GENERAL2 = "Lycée - Seconde"
    GENERAL1 = "Lycée - Première"
    GENERAL0 = "Lycée - Terminale"


class BookingCancellationReasons(enum.Enum):
    OFFERER = "OFFERER"
    BENEFICIARY = "BENEFICIARY"
    EXPIRED = "EXPIRED"
    FRAUD = "FRAUD"
    REFUSED_BY_INSTITUTE = "REFUSED_BY_INSTITUTE"


class Ministry(enum.Enum):
    EDUCATION_NATIONALE = "MENjs"
    MER = "MMe"
    AGRICULTURE = "MAg"
    ARMEES = "MAr"


class BookingStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    USED = "USED"
    CANCELLED = "CANCELLED"
    REIMBURSED = "REIMBURSED"


class EducationalBookingStatus(enum.Enum):
    REFUSED = "REFUSED"


class CollectiveOffer(PcObject, ValidationMixin, AccessibilityMixin, StatusMixin, Model):  # type: ignore[valid-type]
    __tablename__ = "collective_offer"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    offerId = sa.Column(sa.BigInteger, nullable=True)

    isActive = sa.Column(sa.Boolean, nullable=False, server_default=sa.sql.expression.true(), default=True)

    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue = sa.orm.relationship("Venue", foreign_keys=[venueId], back_populates="collectiveOffers")

    name = sa.Column(sa.String(140), nullable=False)

    bookingEmail = sa.Column(sa.String(120), nullable=True)

    description = sa.Column(sa.Text, nullable=True)

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    subcategoryId = sa.Column(sa.Text, nullable=False, index=True)

    dateUpdated: datetime = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    students: list[str] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(StudentLevels))),
        nullable=False,
        server_default="{}",
    )

    collectiveStocks = relationship("CollectiveStock", back_populates="collectiveOffer")

    contactEmail = sa.Column(sa.String(120), nullable=False)

    contactPhone = sa.Column(sa.String(20), nullable=False)

    offerVenue = sa.Column("jsonData", postgresql.JSONB)

    @sa.ext.hybrid.hybrid_property
    def isSoldOut(self):
        # todo redefinir
        for stock in self.stocks:
            if (
                not stock.isSoftDeleted
                and (stock.beginningDatetime is None or stock.beginningDatetime > datetime.utcnow())
                and (stock.remainingQuantity == "unlimited" or stock.remainingQuantity > 0)
            ):
                return False
        return True

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls):  # pylint: disable=no-self-argument
        # TODO redefine
        return (
            ~sa.exists()
            .where(CollectiveStock.offerId == cls.id)
            .where(CollectiveStock.isSoftDeleted.is_(False))
            .where(
                sa.or_(CollectiveStock.beginningDatetime > sa.func.now(), CollectiveStock.beginningDatetime.is_(None))
            )
            .where(sa.or_(CollectiveStock.remainingQuantity.is_(None), CollectiveStock.remainingQuantity > 0))
        )

    @property
    def isBookable(self) -> bool:
        # TODO redifinir
        for stock in self.stocks:
            if stock.isBookable:
                return True
        return False

    @property
    def isReleased(self) -> bool:
        return (
            self.isActive
            and self.validation == OfferValidationStatus.APPROVED
            and self.venue.isValidated
            and self.venue.managingOfferer.isActive
            and self.venue.managingOfferer.isValidated
        )

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if self.activeStocks:
            return all(stock.hasBookingLimitDatetimePassed for stock in self.activeStocks)
        return False

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls):  # pylint: disable=no-self-argument
        return sa.and_(
            sa.exists().where(CollectiveStock.offerId == cls.id).where(CollectiveStock.isSoftDeleted.is_(False)),
            ~sa.exists()
            .where(CollectiveStock.offerId == cls.id)
            .where(CollectiveStock.isSoftDeleted.is_(False))
            .where(CollectiveStock.hasBookingLimitDatetimePassed.is_(False)),
        )


class CollectiveStock(PcObject, Model):  # type: ignore[valid-type]
    __tablename__ = "collective_stock"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    stockId = sa.Column(sa.BigInteger, nullable=True)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now())

    dateModified = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    beginningDatetime = sa.Column(
        sa.DateTime, index=True, nullable=False
    )  #  TODO 4 cas a ratrapper avec un beginDatetime NULL

    collectiveOfferId = sa.Column(sa.BigInteger, sa.ForeignKey("collective_offer.id"), index=True, nullable=False)

    collectiveOffer = sa.orm.relationship(
        "CollectiveOffer", foreign_keys=[collectiveOfferId], back_populates="collectiveStocks"
    )

    price = sa.Column(
        sa.Numeric(10, 2), sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )

    bookingLimitDatetime = sa.Column(sa.DateTime, nullable=False)

    numberOfTickets = sa.Column(sa.Integer, nullable=True)

    priceDetail = sa.Column(sa.Text, nullable=True)

    @property
    def isBookable(self) -> bool:
        return not self.isExpired and self.offer.isReleased and not self.isSoldOut

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimePassed(self):
        return bool(self.bookingLimitDatetime and self.bookingLimitDatetime <= datetime.utcnow())

    @hasBookingLimitDatetimePassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimePassed(cls):  # pylint: disable=no-self-argument
        return sa.and_(cls.bookingLimitDatetime != None, cls.bookingLimitDatetime <= sa.func.now())

    @sa.ext.hybrid.hybrid_property
    def remainingQuantity(self):  # todo rewrite
        return "unlimited" if self.quantity is None else self.quantity - self.dnBookedQuantity

    @remainingQuantity.expression  # type: ignore[no-redef]
    def remainingQuantity(cls):  # pylint: disable=no-self-argument
        return sa.case([(cls.quantity.is_(None), None)], else_=(cls.quantity - cls.dnBookedQuantity))

    @sa.ext.hybrid.hybrid_property
    def isEventExpired(self):  # todo rewrite
        return bool(self.beginningDatetime and self.beginningDatetime <= datetime.utcnow())

    @isEventExpired.expression  # type: ignore[no-redef]
    def isEventExpired(cls):  # pylint: disable=no-self-argument
        return sa.and_(cls.beginningDatetime != None, cls.beginningDatetime <= sa.func.now())

    @property
    def isExpired(self) -> bool:  # todo rewrite
        return self.isEventExpired or self.hasBookingLimitDatetimePassed  # type: ignore[return-value]

    @property
    def isEventDeletable(self) -> bool:  # todo rewrite
        if not self.beginningDatetime:
            return True
        limit_date_for_stock_deletion = self.beginningDatetime
        return limit_date_for_stock_deletion >= datetime.utcnow()

    @property
    def isSoldOut(self) -> bool:
        # pylint: disable=comparison-with-callable
        if (
            not self.isSoftDeleted
            and (self.beginningDatetime is None or self.beginningDatetime > datetime.utcnow())
            and (self.remainingQuantity == "unlimited" or self.remainingQuantity > 0)
        ):
            return False
        return True


class EducationalInstitution(PcObject, Model):  # type: ignore[valid-type]
    __tablename__ = "educational_institution"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    institutionId: str = sa.Column(sa.String(30), nullable=False, unique=True, index=True)


class EducationalYear(PcObject, Model):  # type: ignore[valid-type]
    __tablename__ = "educational_year"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    adageId: str = sa.Column(sa.String(30), unique=True, nullable=False)

    beginningDate: datetime = sa.Column(sa.DateTime, nullable=False)

    expirationDate: datetime = sa.Column(sa.DateTime, nullable=False)


class EducationalDeposit(PcObject, Model):  # type: ignore[valid-type]
    __tablename__ = "educational_deposit"

    TEMPORARY_FUND_AVAILABLE_RATIO = 0.8

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    educationalInstitutionId = sa.Column(
        sa.BigInteger, sa.ForeignKey("educational_institution.id"), index=True, nullable=False
    )

    educationalInstitution: EducationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="deposits"
    )

    educationalYearId = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), index=True, nullable=False)

    educationalYear: EducationalYear = relationship(
        EducationalYear, foreign_keys=[educationalYearId], backref="deposits"
    )

    amount: Decimal = sa.Column(Numeric(10, 2), nullable=False)

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    isFinal: bool = sa.Column(Boolean, nullable=False, default=True)

    ministry = sa.Column(
        sa.Enum(Ministry),
        nullable=True,
    )

    def get_amount(self) -> Decimal:
        return round(self.amount * Decimal(self.TEMPORARY_FUND_AVAILABLE_RATIO), 2) if not self.isFinal else self.amount

    def check_has_enough_fund(self, total_amount_after_booking: Decimal) -> None:
        if self.amount < total_amount_after_booking:
            raise exceptions.InsufficientFund()

        if self.get_amount() < total_amount_after_booking and not self.isFinal:
            raise exceptions.InsufficientTemporaryFund()

        return


class EducationalRedactor(PcObject, Model):  # type: ignore[valid-type]

    __tablename__ = "educational_redactor"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    email: str = sa.Column(sa.String(120), nullable=False, unique=True, index=True)

    firstName: str = sa.Column(sa.String(128), nullable=True)

    lastName: str = sa.Column(sa.String(128), nullable=True)

    civility: str = sa.Column(sa.String(20), nullable=True)

    educationalBookings = relationship(
        "EducationalBooking",
        back_populates="educationalRedactor",
    )


class EducationalBooking(PcObject, Model):  # type: ignore[valid-type]
    __tablename__ = "educational_booking"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    educationalInstitutionId = sa.Column(sa.BigInteger, sa.ForeignKey("educational_institution.id"), nullable=False)
    educationalInstitution: EducationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="educationalBookings"
    )

    educationalYearId = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear: EducationalYear = relationship(EducationalYear, foreign_keys=[educationalYearId])

    Index("ix_educational_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    status = sa.Column(
        "status",
        sa.Enum(EducationalBookingStatus),
        nullable=True,
    )

    confirmationDate: Optional[datetime] = sa.Column(sa.DateTime, nullable=True)
    confirmationLimitDate = sa.Column(sa.DateTime, nullable=True)

    booking = relationship(
        "Booking",
        back_populates="educationalBooking",
        uselist=False,
        lazy="joined",
        innerjoin=True,
    )

    educationalRedactorId = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("educational_redactor.id"),
        nullable=False,
        index=True,
    )
    educationalRedactor: EducationalRedactor = relationship(
        EducationalRedactor,
        back_populates="educationalBookings",
        uselist=False,
    )

    def has_confirmation_limit_date_passed(self) -> bool:
        return bool(self.confirmationLimitDate and self.confirmationLimitDate <= datetime.utcnow())

    def mark_as_refused(self) -> None:
        from pcapi.core.bookings import models as bookings_models

        if (
            self.booking.status != bookings_models.BookingStatus.PENDING
            and self.booking.cancellationLimitDate <= datetime.utcnow()
        ):
            raise exceptions.EducationalBookingNotRefusable()

        try:
            self.booking.cancel_booking()
            self.booking.cancellationReason = bookings_models.BookingCancellationReasons.REFUSED_BY_INSTITUTE
        except booking_exceptions.BookingIsAlreadyUsed:
            raise exceptions.EducationalBookingNotRefusable()
        except booking_exceptions.BookingIsAlreadyCancelled:
            raise exceptions.EducationalBookingAlreadyCancelled()

        self.status = EducationalBookingStatus.REFUSED


class CollectiveBooking(PcObject, Model):  # type: ignore[valid-type]
    __tablename__ = "collective_booking"
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    bookingId = sa.Column(sa.BigInteger)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    Index("ix_collective_booking_date_created", dateCreated)

    dateUsed = sa.Column(sa.DateTime, nullable=True, index=True)

    collectiveStockId = sa.Column(sa.BigInteger, sa.ForeignKey("collective_stock.id"), index=True, nullable=False)

    collectiveStock = relationship("CollectiveStock", foreign_keys=[collectiveStockId], backref="collectiveBookings")

    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)

    venue = relationship("Venue", foreign_keys=[venueId], backref="collectiveBookings")

    offererId = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref="collectiveBookings")

    cancellationDate = sa.Column(sa.DateTime, nullable=True)

    cancellationLimitDate = sa.Column(sa.DateTime, nullable=True)

    cancellationReason = sa.Column(
        "cancellationReason",
        sa.Enum(
            BookingCancellationReasons,
            values_callable=lambda x: [reason.value for reason in BookingCancellationReasons],
        ),
        nullable=True,
    )

    status = sa.Column("status", sa.Enum(BookingStatus), nullable=False, default=BookingStatus.CONFIRMED)

    Index("ix_collective_booking_status", status)

    reimbursementDate = sa.Column(sa.DateTime, nullable=True)

    educationalInstitutionId = sa.Column(sa.BigInteger, sa.ForeignKey("educational_institution.id"), nullable=False)
    educationalInstitution: EducationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="collectiveBookings"
    )

    educationalYearId = sa.Column(sa.String(30), sa.ForeignKey("educational_year.adageId"), nullable=False)
    educationalYear: EducationalYear = relationship(EducationalYear, foreign_keys=[educationalYearId])

    Index("ix_collective_booking_educationalYear_and_institution", educationalYearId, educationalInstitutionId)

    confirmationDate: Optional[datetime] = sa.Column(sa.DateTime, nullable=True)
    confirmationLimitDate = sa.Column(sa.DateTime, nullable=True)

    def mark_as_used(self) -> None:
        if self.is_used_or_reimbursed:  # pylint: disable=using-constant-test
            raise booking_exceptions.BookingHasAlreadyBeenUsed()
        if self.status is BookingStatus.CANCELLED:
            raise booking_exceptions.BookingIsCancelled()
        if self.status is BookingStatus.PENDING:
            raise booking_exceptions.BookingNotConfirmed()
        self.dateUsed = datetime.utcnow()
        self.status = BookingStatus.USED

    def mark_as_unused_set_confirmed(self) -> None:
        self.dateUsed = None
        self.status = BookingStatus.CONFIRMED

    def cancel_booking(self, cancel_even_if_used: bool = False) -> None:
        if self.status is BookingStatus.CANCELLED:
            raise booking_exceptions.BookingIsAlreadyCancelled()
        if self.status is BookingStatus.REIMBURSED:
            raise booking_exceptions.BookingIsAlreadyUsed()
        if self.status is BookingStatus.USED and not cancel_even_if_used:
            raise booking_exceptions.BookingIsAlreadyUsed()
        self.status = BookingStatus.CANCELLED
        self.cancellationDate = datetime.utcnow()

    def uncancel_booking_set_used(self) -> None:
        if not (self.status is BookingStatus.CANCELLED):
            raise booking_exceptions.BookingIsNotCancelledCannotBeUncancelled()
        self.cancellationDate = None
        self.cancellationReason = None
        self.status = BookingStatus.USED
        self.dateUsed = datetime.utcnow()

    def mark_as_confirmed(self) -> None:
        if self.has_confirmation_limit_date_passed():
            raise booking_exceptions.ConfirmationLimitDateHasPassed()

        self.status = BookingStatus.CONFIRMED
        self.confirmationDate = datetime.utcnow()

    @hybrid_property
    def isConfirmed(self):
        return self.cancellationLimitDate is not None and self.cancellationLimitDate <= datetime.utcnow()

    @isConfirmed.expression  # type: ignore[no-redef]
    def isConfirmed(cls):  # pylint: disable=no-self-argument
        return sa.and_(cls.cancellationLimitDate.isnot(None), cls.cancellationLimitDate <= datetime.utcnow())

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [BookingStatus.USED, BookingStatus.REIMBURSED]

    @is_used_or_reimbursed.expression  # type: ignore[no-redef]
    def is_used_or_reimbursed(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.status.in_([BookingStatus.USED, BookingStatus.REIMBURSED])

    @property
    def userName(self) -> Optional[str]:
        if self.individualBooking is not None:
            return f"{self.individualBooking.user.firstName} {self.individualBooking.user.lastName}"

        if self.educationalBooking is not None:
            return f"{self.educationalBooking.educationalRedactor.firstName} {self.educationalBooking.educationalRedactor.lastName}"

        return None

    def has_confirmation_limit_date_passed(self) -> bool:
        return bool(self.confirmationLimitDate and self.confirmationLimitDate <= datetime.utcnow())

    def mark_as_refused(self) -> None:
        from pcapi.core.bookings import models as bookings_models

        if (
            self.booking.status != bookings_models.BookingStatus.PENDING
            and self.booking.cancellationLimitDate <= datetime.utcnow()
        ):
            raise exceptions.EducationalBookingNotRefusable()

        try:
            self.booking.cancel_booking()
            self.booking.cancellationReason = bookings_models.BookingCancellationReasons.REFUSED_BY_INSTITUTE
        except booking_exceptions.BookingIsAlreadyUsed:
            raise exceptions.EducationalBookingNotRefusable()
        except booking_exceptions.BookingIsAlreadyCancelled:
            raise exceptions.EducationalBookingAlreadyCancelled()

        self.status = EducationalBookingStatus.REFUSED


CollectiveBooking.trig_ddl = f"""
    CREATE OR REPLACE FUNCTION public.get_deposit_balance (deposit_id bigint, only_used_bookings boolean)
        RETURNS numeric
        AS $$
    DECLARE
        deposit_amount bigint := (SELECT CASE WHEN ("expirationDate" > now() OR "expirationDate" IS NULL) THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
        sum_bookings numeric;
    BEGIN
        IF deposit_amount IS NULL
        THEN RAISE EXCEPTION 'the deposit was not found';
        END IF;

        SELECT
            COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
        FROM
            booking
            JOIN individual_booking ON (booking."individualBookingId" = individual_booking.id)
        WHERE
            individual_booking."depositId" = deposit_id
            AND NOT booking.status = '{BookingStatus.CANCELLED.value}'
            AND (NOT only_used_bookings OR booking.status in ('USED', 'REIMBURSED'));
        RETURN
            deposit_amount - sum_bookings;
        END;
    $$
    LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION public.get_wallet_balance (user_id bigint, only_used_bookings boolean)
        RETURNS numeric
        AS $$
    DECLARE
        deposit_id bigint := (SELECT deposit.id FROM deposit WHERE "userId" = user_id  AND "expirationDate" > now());
    BEGIN
        RETURN
            CASE WHEN deposit_id IS NOT NULL THEN get_deposit_balance(deposit_id, only_used_bookings) ELSE 0 END;
    END;
    $$
    LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    DECLARE
        lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
        deposit_id bigint := (SELECT individual_booking."depositId" FROM booking LEFT JOIN individual_booking ON individual_booking.id = booking."individualBookingId" WHERE booking.id=NEW.id);
    BEGIN
    IF EXISTS (SELECT "quantity" FROM stock WHERE id=NEW."stockId" AND "quantity" IS NOT NULL)
        AND (
            (SELECT "quantity" FROM stock WHERE id=NEW."stockId")
            <
            (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND status != '{BookingStatus.CANCELLED.value}')
            )
        THEN RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.quantity"';
    END IF;

    IF (
        (NEW."educationalBookingId" IS NULL AND OLD."educationalBookingId" IS NULL)
        AND (NEW."individualBookingId" IS NOT NULL OR OLD."individualBookingId" IS NOT NULL)
        AND (
        -- If this is a new booking, we probably want to check the wallet.
        OLD IS NULL
        -- If we're updating an existing booking...
        OR (
            -- Check the wallet if we are changing the quantity or the amount
            -- The backend should never do that, but let's be defensive.
            (NEW."quantity" != OLD."quantity" OR NEW."amount" != OLD."amount")
            -- If amount and quantity are unchanged, we want to check the wallet
            -- only if we are UNcancelling a booking. (Users with no credits left
            -- should be able to cancel their booking. Also, their booking can
            -- be marked as used or not used.)
            OR (NEW.status != OLD.status AND OLD.status = '{BookingStatus.CANCELLED.value}' AND NEW.status != '{BookingStatus.CANCELLED.value}')
        )
        )
        AND (
            -- Allow to book free offers even with no credit left (or expired deposits)
            (deposit_id IS NULL AND NEW."amount" != 0)
            OR (deposit_id IS NOT NULL AND get_deposit_balance(deposit_id, false) < 0)
        )
    )
    THEN RAISE EXCEPTION 'insufficientFunds'
                USING HINT = 'The user does not have enough credit to book';
    END IF;

    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS booking_update ON booking;
    CREATE CONSTRAINT TRIGGER booking_update
    AFTER INSERT
    OR UPDATE OF quantity, amount, status, "userId"
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
sa.event.listen(CollectiveBooking.__table__, "after_create", sa.DDL(CollectiveBooking.trig_ddl))

CollectiveBooking.trig_update_cancellationDate_on_isCancelled_ddl = f"""
    CREATE OR REPLACE FUNCTION save_cancellation_date()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.status = '{BookingStatus.CANCELLED.value}' AND OLD."cancellationDate" IS NULL AND NEW."cancellationDate" THEN
            NEW."cancellationDate" = NOW();
        ELSIF NEW.status != '{BookingStatus.CANCELLED.value}' THEN
            NEW."cancellationDate" = NULL;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS stock_update_cancellation_date ON booking;

    CREATE TRIGGER stock_update_cancellation_date
    BEFORE INSERT OR UPDATE OF status ON booking
    FOR EACH ROW
    EXECUTE PROCEDURE save_cancellation_date()
    """

sa.event.listen(
    CollectiveBooking.__table__,
    "after_create",
    sa.DDL(CollectiveBooking.trig_update_cancellationDate_on_isCancelled_ddl),
)


@dataclasses.dataclass
class AdageApiResult:
    sent_data: dict
    response: dict
    success: bool
