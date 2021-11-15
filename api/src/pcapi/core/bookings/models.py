from datetime import datetime
from decimal import Decimal
import enum
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DDL
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import and_
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from pcapi.core.bookings import exceptions
from pcapi.core.bookings.constants import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.categories import subcategories
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.offers.models import Mediation
from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.human_ids import humanize


class BookingCancellationReasons(enum.Enum):
    OFFERER = "OFFERER"
    BENEFICIARY = "BENEFICIARY"
    EXPIRED = "EXPIRED"
    FRAUD = "FRAUD"
    REFUSED_BY_INSTITUTE = "REFUSED_BY_INSTITUTE"


class BookingStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    USED = "USED"
    CANCELLED = "CANCELLED"
    REIMBURSED = "REIMBURSED"


class IndividualBooking(PcObject, Model):
    __tablename__ = "individual_booking"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    userId = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)
    user = relationship(
        "User",
        foreign_keys=[userId],
        backref="userIndividualBookings",
        lazy="joined",
        innerjoin=True,
    )

    depositId = Column(BigInteger, ForeignKey("deposit.id"), index=True, nullable=True)
    deposit = relationship("Deposit", back_populates="individual_bookings")

    booking = relationship(
        "Booking",
        back_populates="individualBooking",
        uselist=False,
        lazy="joined",
        innerjoin=True,
    )


class Booking(PcObject, Model):
    __tablename__ = "booking"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow)

    dateUsed = Column(DateTime, nullable=True, index=True)

    stockId = Column(BigInteger, ForeignKey("stock.id"), index=True, nullable=False)

    stock = relationship("Stock", foreign_keys=[stockId], backref="bookings")

    venueId = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)

    venue = relationship("Venue", foreign_keys=[venueId], backref="bookings")

    offererId = Column(BigInteger, ForeignKey("offerer.id"), index=True, nullable=False)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref="bookings")

    quantity = Column(Integer, nullable=False, default=1)

    token = Column(String(6), unique=True, nullable=False)

    userId = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=True)

    activationCode = relationship("ActivationCode", uselist=False, back_populates="booking")

    user = relationship("User", foreign_keys=[userId], backref="userBookings")

    amount = Column(Numeric(10, 2), nullable=False)

    isCancelled = Column(Boolean, nullable=False, server_default=expression.false(), default=False)

    cancellationDate = Column(DateTime, nullable=True)

    isUsed = Column(Boolean, nullable=False, default=False, server_default=expression.false())

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

    status = Column("status", Enum(BookingStatus), nullable=True, default=BookingStatus.CONFIRMED)

    reimbursementDate = Column(DateTime, nullable=True)

    educationalBookingId = Column(
        BigInteger,
        ForeignKey("educational_booking.id"),
        nullable=True,
        unique=True,
        index=True,
    )
    educationalBooking: Optional[EducationalBooking] = relationship(
        EducationalBooking,
        back_populates="booking",
        uselist=False,
    )

    individualBookingId = Column(
        BigInteger,
        ForeignKey("individual_booking.id"),
        nullable=True,
        unique=True,
        index=True,
    )
    individualBooking: Optional[IndividualBooking] = relationship(
        IndividualBooking,
        back_populates="booking",
        uselist=False,
    )

    def mark_as_used(self) -> None:
        if self.status is BookingStatus.USED or self.isUsed:
            raise exceptions.BookingHasAlreadyBeenUsed()
        if self.status is BookingStatus.CANCELLED or self.isCancelled:
            raise exceptions.BookingIsCancelled()
        self.isUsed = True
        self.dateUsed = datetime.utcnow()
        self.status = BookingStatus.USED

    def mark_as_unused_set_confirmed(self) -> None:
        self.isUsed = False
        self.dateUsed = None
        self.status = BookingStatus.CONFIRMED

    def cancel_booking(self) -> None:
        if self.status is BookingStatus.CANCELLED or self.isCancelled:
            raise exceptions.BookingIsAlreadyCancelled()
        if self.status is BookingStatus.USED or self.isUsed:
            raise exceptions.BookingIsAlreadyUsed()
        self.isCancelled = True
        self.status = BookingStatus.CANCELLED
        self.cancellationDate = datetime.utcnow()

    def uncancel_booking_set_used(self) -> None:
        if not (self.status is BookingStatus.CANCELLED or self.isCancelled):
            raise exceptions.BookingIsNotCancelledCannotBeUncancelled()
        self.isCancelled = False
        self.cancellationDate = None
        self.cancellationReason = None
        self.status = BookingStatus.USED
        self.isUsed = True
        self.dateUsed = datetime.utcnow()

    def mark_as_confirmed(self) -> None:
        if self.educationalBooking is None:
            raise exceptions.CannotMarkAsConfirmedIndividualBooking()
        if self.educationalBooking.has_confirmation_limit_date_passed():
            raise exceptions.ConfirmationLimitDateHasPassed()

        self.status = BookingStatus.CONFIRMED
        self.educationalBooking.confirmationDate = datetime.utcnow()

    @property
    def expirationDate(self) -> Optional[datetime]:
        if self.isCancelled or self.isUsed:
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
    def completedUrl(self) -> Optional[str]:
        offer = self.stock.offer
        url = offer.url
        if url is None:
            return None
        if not url.startswith("http"):
            url = "http://" + url

        token = self.activationCode.code if self.activationCode else self.token

        return url.replace("{token}", token).replace("{offerId}", humanize(offer.id)).replace("{email}", self.email)

    @staticmethod
    def restize_internal_error(ie: Exception) -> list[str]:
        if "tooManyBookings" in str(ie.orig):
            return ["global", "La quantité disponible pour cette offre est atteinte."]
        if "insufficientFunds" in str(ie.orig):
            return ["insufficientFunds", "Le solde de votre pass est insuffisant pour réserver cette offre."]
        return PcObject.restize_integrity_error(ie)

    @property
    def isEventExpired(self) -> bool:
        return self.stock.isEventExpired

    @property
    def thumbUrl(self) -> str:
        if self.mediation:
            return self.mediation.thumbUrl
        return self.stock.offer.product.thumbUrl

    @property
    def mediation(self) -> Optional[Mediation]:
        return self.stock.offer.activeMediation

    @property
    def qrCode(self) -> Optional[str]:
        from . import api  # avoid import loop

        offer = self.stock.offer
        if offer.isEvent:
            if self.isEventExpired or self.isCancelled:
                return None
            return api.generate_qr_code(self.token)
        if self.isUsed or self.isCancelled:
            return None
        return api.generate_qr_code(self.token)

    @hybrid_property
    def isConfirmed(self):
        return self.cancellationLimitDate is not None and self.cancellationLimitDate <= datetime.utcnow()

    @isConfirmed.expression
    def isConfirmed(cls):  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return and_(cls.cancellationLimitDate.isnot(None), cls.cancellationLimitDate <= datetime.utcnow())

    @property
    def firstName(self) -> Optional[str]:
        if self.individualBooking is not None:
            return self.individualBooking.user.firstName

        if self.educationalBooking is not None:
            return self.educationalBooking.educationalRedactor.firstName

        return None

    @property
    def lastName(self) -> Optional[str]:
        if self.individualBooking is not None:
            return self.individualBooking.user.lastName

        if self.educationalBooking is not None:
            return self.educationalBooking.educationalRedactor.lastName

        return None

    @property
    def publicName(self) -> Optional[str]:
        if self.individualBooking is not None:
            return self.individualBooking.user.publicName

        if self.educationalBooking is not None:
            return f"{self.educationalBooking.educationalRedactor.firstName} {self.educationalBooking.educationalRedactor.lastName}"

        return None

    @property
    def email(self) -> Optional[str]:
        if self.individualBooking is not None:
            return self.individualBooking.user.email

        if self.educationalBooking is not None:
            return self.educationalBooking.educationalRedactor.email

        return None


# FIXME (dbaty, 2020-02-08): once `Deposit.expirationDate` has been
# populated after the deployment of v122, make the column NOT NULLable
# and remove the filter below (add a migration for _each_ change).
Booking.trig_ddl = """
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
            AND NOT booking."isCancelled"
            AND (NOT only_used_bookings OR booking."isUsed" = TRUE);
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
            (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND NOT "isCancelled")
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
            OR (NEW."isCancelled" != OLD."isCancelled" AND NOT NEW."isCancelled")
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
    OR UPDATE OF quantity, amount, "isCancelled", "isUsed", "userId"
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
event.listen(Booking.__table__, "after_create", DDL(Booking.trig_ddl))

Booking.trig_update_cancellationDate_on_isCancelled_ddl = """
    CREATE OR REPLACE FUNCTION save_cancellation_date()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW."isCancelled" IS TRUE AND OLD."cancellationDate" IS NULL THEN
            NEW."cancellationDate" = NOW();
        ELSIF NEW."isCancelled" IS FALSE THEN
            NEW."cancellationDate" = NULL;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS stock_update_cancellation_date ON booking;

    -- XXX: update anonymize SQL script if you change anything below
    CREATE TRIGGER stock_update_cancellation_date
    BEFORE INSERT OR UPDATE ON booking
    FOR EACH ROW
    EXECUTE PROCEDURE save_cancellation_date()
    """

event.listen(Booking.__table__, "after_create", DDL(Booking.trig_update_cancellationDate_on_isCancelled_ddl))
