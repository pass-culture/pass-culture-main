from datetime import datetime
import decimal
from decimal import Decimal
import enum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DDL
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import event
from sqlalchemy import exists
from sqlalchemy import select
import sqlalchemy.exc as sa_exc
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import Label

from pcapi.core.bookings import exceptions
from pcapi.core.bookings.constants import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.categories import subcategories
import pcapi.core.finance.models as finance_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.human_ids import humanize


if TYPE_CHECKING:
    from pcapi.core.finance.models import Deposit
    from pcapi.core.offerers import models as offerers_models
    from pcapi.core.offers import models as offers_models
    from pcapi.core.users import models as users_models


class BookingCancellationReasons(enum.Enum):
    OFFERER = "OFFERER"
    BENEFICIARY = "BENEFICIARY"
    EXPIRED = "EXPIRED"
    FRAUD = "FRAUD"
    REFUSED_BY_INSTITUTE = "REFUSED_BY_INSTITUTE"


class BookingStatus(enum.Enum):
    CONFIRMED = "CONFIRMED"
    USED = "USED"
    CANCELLED = "CANCELLED"
    REIMBURSED = "REIMBURSED"


class BookingStatusFilter(enum.Enum):
    BOOKED = "booked"
    VALIDATED = "validated"
    REIMBURSED = "reimbursed"


class BookingExportType(enum.Enum):
    CSV = "csv"
    EXCEL = "excel"


class ExternalBooking(PcObject, Base, Model):
    bookingId: int = Column(BigInteger, ForeignKey("booking.id"), index=True, nullable=False)

    booking: Mapped["Booking"] = relationship("Booking", foreign_keys=[bookingId], backref="externalBookings")

    barcode: str = Column(String, nullable=False)

    seat = Column(String)


class Booking(PcObject, Base, Model):
    __tablename__ = "booking"

    dateCreated: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    Index("ix_booking_date_created", dateCreated)

    dateUsed = Column(DateTime, nullable=True, index=True)

    stockId: int = Column(BigInteger, ForeignKey("stock.id"), index=True, nullable=False)

    stock: Mapped["offers_models.Stock"] = relationship("Stock", foreign_keys=[stockId], backref="bookings")

    venueId: int = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)

    venue: Mapped["offerers_models.Venue"] = relationship("Venue", foreign_keys=[venueId], backref="bookings")

    offererId: int = Column(BigInteger, ForeignKey("offerer.id"), index=True, nullable=False)

    offerer: Mapped["offerers_models.Offerer"] = relationship("Offerer", foreign_keys=[offererId], backref="bookings")

    quantity: int = Column(Integer, nullable=False, default=1)

    token: str = Column(String(6), unique=True, nullable=False)

    userId: int = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)

    activationCode = relationship("ActivationCode", uselist=False, back_populates="booking")  # type: ignore [misc]

    user: Mapped["users_models.User"] = relationship("User", foreign_keys=[userId], backref="userBookings")

    amount: Decimal = Column(Numeric(10, 2), nullable=False)

    priceCategoryLabel: str | None = Column(Text, nullable=True)

    cancellationDate = Column(DateTime, nullable=True)

    displayAsEnded = Column(Boolean, nullable=True)

    cancellationLimitDate = Column(DateTime, nullable=True)

    cancellationReason = Column(
        "cancellationReason",
        Enum(
            BookingCancellationReasons,
            values_callable=lambda x: [reason.value for reason in BookingCancellationReasons],
        ),
        nullable=True,
    )

    status: BookingStatus = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.CONFIRMED)
    Index("ix_booking_status", status)

    reimbursementDate = Column(DateTime, nullable=True, index=True)

    depositId = Column(BigInteger, ForeignKey("deposit.id"), index=True, nullable=True)

    deposit: Mapped["Deposit | None"] = relationship("Deposit", foreign_keys=[depositId], back_populates="bookings")

    def mark_as_used(self) -> None:
        if self.is_used_or_reimbursed:
            raise exceptions.BookingHasAlreadyBeenUsed()
        if self.status is BookingStatus.CANCELLED:
            raise exceptions.BookingIsCancelled()
        self.dateUsed = datetime.utcnow()
        self.status = BookingStatus.USED

    def mark_as_unused_set_confirmed(self) -> None:
        self.dateUsed = None
        self.status = BookingStatus.CONFIRMED

    def cancel_booking(
        self,
        reason: BookingCancellationReasons,
        cancel_even_if_used: bool = False,
    ) -> None:
        if self.status is BookingStatus.CANCELLED:
            raise exceptions.BookingIsAlreadyCancelled()
        if self.status is BookingStatus.REIMBURSED:
            raise exceptions.BookingIsAlreadyUsed()
        if self.status is BookingStatus.USED and not cancel_even_if_used:
            raise exceptions.BookingIsAlreadyUsed()
        self.status = BookingStatus.CANCELLED
        self.cancellationDate = datetime.utcnow()
        self.cancellationReason = reason
        self.dateUsed = None

    def uncancel_booking_set_used(self) -> None:
        if not (self.status is BookingStatus.CANCELLED):
            raise exceptions.BookingIsNotCancelledCannotBeUncancelled()
        self.cancellationDate = None
        self.cancellationReason = None
        self.status = BookingStatus.USED
        self.dateUsed = datetime.utcnow()

    @property
    def expirationDate(self) -> datetime | None:
        if self.status == BookingStatus.CANCELLED or self.is_used_or_reimbursed:
            return None
        if not self.stock.offer.canExpire:
            return None
        if self.stock.offer.subcategoryId == subcategories.LIVRE_PAPIER.id:
            return self.dateCreated + BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
        return self.dateCreated + BOOKINGS_AUTO_EXPIRY_DELAY

    @property
    def total_amount(self) -> Decimal:
        return self.amount * self.quantity

    # FIXME: many functions here are only used when serializing
    # bookings in the web API. They can be moved elsewhere once we
    # have replaced the auto-magic serialization ("includes").
    @property
    def completedUrl(self) -> str | None:
        offer = self.stock.offer
        url = offer.url
        if url is None:
            return None
        if not url.startswith("http"):
            url = "http://" + url

        token = self.activationCode.code if self.activationCode else self.token

        return url.replace("{token}", token).replace("{offerId}", humanize(offer.id)).replace("{email}", self.email)

    @staticmethod
    def restize_internal_error(ie: sa_exc.InternalError) -> tuple[str, str]:
        assert ie.orig  # helps mypy
        if "tooManyBookings" in str(ie.orig):
            return ("global", "La quantité disponible pour cette offre est atteinte.")
        if "insufficientFunds" in str(ie.orig):
            return ("insufficientFunds", "Le solde de votre pass est insuffisant pour réserver cette offre.")
        return PcObject.restize_internal_error(ie)

    @hybrid_property
    def isConfirmed(self) -> bool:
        return self.cancellationLimitDate is not None and self.cancellationLimitDate <= datetime.utcnow()

    @isConfirmed.expression  # type: ignore [no-redef]
    def isConfirmed(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return and_(cls.cancellationLimitDate.isnot(None), cls.cancellationLimitDate <= datetime.utcnow())

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [BookingStatus.USED, BookingStatus.REIMBURSED]

    @is_used_or_reimbursed.expression  # type: ignore [no-redef]
    def is_used_or_reimbursed(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.status.in_([BookingStatus.USED, BookingStatus.REIMBURSED])

    @hybrid_property
    def isReimbursed(self) -> bool:
        return self.status == BookingStatus.REIMBURSED

    @isReimbursed.expression  # type: ignore [no-redef]
    def isReimbursed(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.status == BookingStatus.REIMBURSED

    @hybrid_property
    def isCancelled(self) -> bool:
        return self.status == BookingStatus.CANCELLED

    @isCancelled.expression  # type: ignore [no-redef]
    def isCancelled(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.status == BookingStatus.CANCELLED

    @property
    def firstName(self) -> str | None:
        return self.user.firstName

    @property
    def lastName(self) -> str | None:
        return self.user.lastName

    @property
    def userName(self) -> str:
        return self.user.full_name

    @property
    def email(self) -> str:
        return self.user.email

    @property
    def emailAtDateCreated(self) -> str:
        email = self.user.email
        for email_history in sorted(self.user.email_history, key=lambda history: history.creationDate):
            if self.dateCreated < email_history.creationDate:
                email = email_history.oldEmail
                break
        return email

    @hybrid_property
    def isExternal(self) -> bool:
        return any(externalBooking.id for externalBooking in self.externalBookings)

    @isExternal.expression  # type: ignore [no-redef]
    def isExternal(cls) -> Label:  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return select(
            [
                case(
                    [(exists().where(ExternalBooking.bookingId == cls.id).correlate(cls), True)],
                    else_=False,
                ).label("isExternal")
            ]
        ).label("number_of_externalBookings")

    @property
    def pricing(self) -> finance_models.Pricing | None:
        processed_pricings = [
            pricing for pricing in self.pricings if pricing.status == finance_models.PricingStatus.INVOICED
        ]

        pricings = sorted(processed_pricings, key=lambda x: x.creationDate, reverse=True)
        if pricings:
            return pricings[0]

        return None

    @property
    def cashflow_batch(self) -> finance_models.CashflowBatch | None:
        if not self.pricing:
            return None

        cashflow = self.pricing.cashflow
        if not cashflow:
            return None

        return cashflow.batch

    @property
    def reimbursement_rate(self) -> float | None:
        if not self.pricing:
            return None

        try:
            # pricing.amount is in cents, amount in euros
            # -> the result is a percentage
            return float("{:.2f}".format((-self.pricing.amount / self.amount)))
        except (decimal.DivisionByZero, decimal.InvalidOperation):  # raised when both values are 0
            return None


Booking.trig_ddl = f"""
    CREATE OR REPLACE FUNCTION public.get_deposit_balance (deposit_id bigint, only_used_bookings boolean)
        RETURNS numeric
        AS $$
    DECLARE
        deposit_amount bigint := (SELECT CASE WHEN "expirationDate" > now() THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
        sum_bookings numeric;
    BEGIN
        IF deposit_amount IS NULL
        THEN RAISE EXCEPTION 'the deposit was not found';
        END IF;

        SELECT
            COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
        FROM
            booking
        WHERE
            booking."depositId" = deposit_id
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
        deposit_id bigint := (SELECT booking."depositId" FROM booking WHERE booking.id=NEW.id);
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
        (
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
event.listen(Booking.__table__, "after_create", DDL(Booking.trig_ddl))

Booking.trig_update_cancellationDate_on_isCancelled_ddl = f"""
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

event.listen(Booking.__table__, "after_create", DDL(Booking.trig_update_cancellationDate_on_isCancelled_ddl))
