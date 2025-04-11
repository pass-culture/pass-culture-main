from datetime import datetime
import decimal
from decimal import Decimal
import enum
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.exc as sa_exc
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import Label

from pcapi.core.bookings import exceptions
from pcapi.core.bookings.constants import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.utils import SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE
from pcapi.core.bookings.utils import get_cooldown_datetime_by_subcategories
from pcapi.core.categories import subcategories
import pcapi.core.finance.models as finance_models
from pcapi.core.offers import models as offers_models
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.users import models as users_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.db import MagicEnum
from pcapi.utils.human_ids import humanize


if TYPE_CHECKING:
    from pcapi.core.offerers import models as offerers_models


class BookingCancellationReasons(enum.Enum):
    OFFERER = "OFFERER"
    BENEFICIARY = "BENEFICIARY"
    EXPIRED = "EXPIRED"
    FRAUD = "FRAUD"
    FRAUD_SUSPICION = "FRAUD_SUSPICION"
    FRAUD_INAPPROPRIATE = "FRAUD_INAPPROPRIATE"
    REFUSED_BY_INSTITUTE = "REFUSED_BY_INSTITUTE"
    FINANCE_INCIDENT = "FINANCE_INCIDENT"
    BACKOFFICE = "BACKOFFICE"
    BACKOFFICE_EVENT_CANCELLED = "BACKOFFICE_EVENT_CANCELLED"
    BACKOFFICE_OVERBOOKING = "BACKOFFICE_OVERBOOKING"
    BACKOFFICE_BENEFICIARY_REQUEST = "BACKOFFICE_BENEFICIARY_REQUEST"
    BACKOFFICE_OFFER_MODIFIED = "BACKOFFICE_OFFER_MODIFIED"
    BACKOFFICE_OFFER_WITH_WRONG_INFORMATION = "BACKOFFICE_OFFER_WITH_WRONG_INFORMATION"
    BACKOFFICE_OFFERER_BUSINESS_CLOSED = "BACKOFFICE_OFFERER_BUSINESS_CLOSED"
    OFFERER_CONNECT_AS = "OFFERER_CONNECT_AS"
    OFFERER_CLOSED = "OFFERER_CLOSED"

    @classmethod
    def is_from_backoffice(cls, reason: "BookingCancellationReasons") -> bool:
        return reason in (
            cls.BACKOFFICE,
            cls.BACKOFFICE_EVENT_CANCELLED,
            cls.BACKOFFICE_OVERBOOKING,
            cls.BACKOFFICE_BENEFICIARY_REQUEST,
            cls.BACKOFFICE_OFFER_MODIFIED,
            cls.BACKOFFICE_OFFER_WITH_WRONG_INFORMATION,
            cls.BACKOFFICE_OFFERER_BUSINESS_CLOSED,
            cls.FRAUD,
            cls.FRAUD_SUSPICION,
            cls.FRAUD_INAPPROPRIATE,
        )


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


class BookingValidationAuthorType(enum.Enum):
    OFFERER = "OFFERER"
    BACKOFFICE = "BACKOFFICE"
    AUTO = "AUTO"


class BookingRecreditType(enum.Enum):
    RECREDIT_17 = "RECREDIT_17"
    RECREDIT_18 = "RECREDIT_18"


class ExternalBooking(PcObject, Base, Model):
    bookingId: int = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=False)

    booking: sa_orm.Mapped["Booking"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], backref="externalBookings"
    )

    barcode: str = sa.Column(sa.String, nullable=False)

    seat = sa.Column(sa.String)

    additional_information: dict | None = sa.Column(postgresql.JSONB)


class Booking(PcObject, Base, Model):
    __tablename__ = "booking"

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    sa.Index("ix_booking_date_created", dateCreated)

    dateUsed: datetime | None = sa.Column(sa.DateTime, nullable=True, index=True)

    stockId: int = sa.Column(sa.BigInteger, sa.ForeignKey("stock.id"), index=True, nullable=False)

    stock: sa_orm.Mapped["offers_models.Stock"] = sa_orm.relationship(
        "Stock", foreign_keys=[stockId], backref="bookings"
    )

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)

    venue: sa_orm.Mapped["offerers_models.Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], backref="bookings"
    )

    offererId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False)

    offerer: sa_orm.Mapped["offerers_models.Offerer"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], backref="bookings"
    )

    quantity: int = sa.Column(sa.Integer, nullable=False, default=1)

    token: str = sa.Column(sa.String(6), unique=True, nullable=False)

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    activationCode: sa_orm.Mapped["offers_models.ActivationCode"] = sa_orm.relationship(
        "ActivationCode", uselist=False, back_populates="booking"
    )

    user: sa_orm.Mapped["users_models.User"] = sa_orm.relationship(
        "User", foreign_keys=[userId], backref="userBookings"
    )

    amount: Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)

    priceCategoryLabel: str | None = sa.Column(sa.Text, nullable=True)

    cancellationDate: datetime | None = sa.Column(sa.DateTime, nullable=True)

    displayAsEnded = sa.Column(sa.Boolean, nullable=True)

    cancellationLimitDate = sa.Column(sa.DateTime, nullable=True)

    cancellationReason = sa.Column(
        "cancellationReason",
        sa.Enum(
            BookingCancellationReasons,
            values_callable=lambda x: [reason.value for reason in BookingCancellationReasons],
        ),
        nullable=True,
    )
    sa.Index(
        "ix_booking_cancellation_reason",
        cancellationReason,
        postgresql_where=cancellationReason.is_not(None),
    )

    cancellationUserId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)
    cancellationUser: sa_orm.Mapped["users_models.User | None"] = sa_orm.relationship(
        "User", foreign_keys=[cancellationUserId]
    )
    # Index avoids timeout when any user is deleted (because of foreign key)
    sa.Index("ix_booking_cancellationUserId", cancellationUserId, postgresql_where=cancellationUserId.is_not(None))

    status: BookingStatus = sa.Column(sa.Enum(BookingStatus), nullable=False, default=BookingStatus.CONFIRMED)
    sa.Index("ix_booking_status", status)

    validationAuthorType: BookingValidationAuthorType = sa.Column(sa.Enum(BookingValidationAuthorType), nullable=True)

    reimbursementDate = sa.Column(sa.DateTime, nullable=True)

    depositId = sa.Column(sa.BigInteger, sa.ForeignKey("deposit.id"), index=True, nullable=True)

    deposit: sa_orm.Mapped["finance_models.Deposit | None"] = sa_orm.relationship(
        "Deposit", foreign_keys=[depositId], back_populates="bookings"
    )

    usedRecreditType: BookingRecreditType = sa.Column(MagicEnum(BookingRecreditType), nullable=True)

    fraudulentBookingTag: sa_orm.Mapped["FraudulentBookingTag"] = sa_orm.relationship(
        "FraudulentBookingTag", back_populates="booking", uselist=False
    )

    def mark_as_used(self, validation_author_type: BookingValidationAuthorType) -> None:
        if self.is_used_or_reimbursed:
            raise exceptions.BookingHasAlreadyBeenUsed()
        if self.status is BookingStatus.CANCELLED:
            raise exceptions.BookingIsCancelled()
        self.dateUsed = datetime.utcnow()
        self.status = BookingStatus.USED
        self.validationAuthorType = validation_author_type

    def mark_as_unused_set_confirmed(self) -> None:
        self.dateUsed = None
        self.status = BookingStatus.CONFIRMED

    def cancel_booking(
        self,
        reason: BookingCancellationReasons,
        cancel_even_if_used: bool = False,
        cancel_even_if_reimbursed: bool = False,
        author_id: int | None = None,
    ) -> None:
        if self.status is BookingStatus.CANCELLED:
            raise exceptions.BookingIsAlreadyCancelled()
        if self.status is BookingStatus.REIMBURSED and not cancel_even_if_reimbursed:
            raise exceptions.BookingIsAlreadyUsed()
        if self.status is BookingStatus.USED and not cancel_even_if_used:
            raise exceptions.BookingIsAlreadyUsed()
        self.status = BookingStatus.CANCELLED
        self.cancellationDate = datetime.utcnow()
        self.cancellationReason = reason
        self.cancellationUserId = author_id
        self.dateUsed = None

    def uncancel_booking_set_used(self) -> None:
        if self.status is not BookingStatus.CANCELLED:
            raise exceptions.BookingIsNotCancelledCannotBeUncancelled()
        self.cancellationDate = None
        self.cancellationReason = None
        self.cancellationUserId = None
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

    @hybrid_property
    def total_amount(self) -> Decimal:
        return self.amount * self.quantity

    @property
    def completedUrl(self) -> str | None:
        offer = self.stock.offer
        url = offer.url
        if url is None:
            return None
        if not url.startswith("http"):
            url = "http://" + url

        token = self.activationCode.code if self.activationCode else self.token

        humanized_offer_id = humanize(offer.id)
        assert humanized_offer_id  # helps mypy
        return url.replace("{token}", token).replace("{offerId}", humanized_offer_id).replace("{email}", self.email)

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

    @isConfirmed.expression  # type: ignore[no-redef]
    def isConfirmed(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls.cancellationLimitDate.is_not(None), cls.cancellationLimitDate <= sa.func.now())

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [BookingStatus.USED, BookingStatus.REIMBURSED]

    @is_used_or_reimbursed.expression  # type: ignore[no-redef]
    def is_used_or_reimbursed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.status.in_([BookingStatus.USED, BookingStatus.REIMBURSED])

    @hybrid_property
    def isReimbursed(self) -> bool:
        return self.status == BookingStatus.REIMBURSED

    @isReimbursed.expression  # type: ignore[no-redef]
    def isReimbursed(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.status == BookingStatus.REIMBURSED

    @hybrid_property
    def isCancelled(self) -> bool:
        return self.status == BookingStatus.CANCELLED

    @isCancelled.expression  # type: ignore[no-redef]
    def isCancelled(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
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

    @hybrid_property
    def isExternal(self) -> bool:
        return any(externalBooking.id for externalBooking in self.externalBookings)

    @isExternal.expression  # type: ignore[no-redef]
    def isExternal(cls) -> Label:  # pylint: disable=no-self-argument
        return sa.select(
            sa.case(
                (sa.exists().where(ExternalBooking.bookingId == cls.id).correlate(cls), True),
                else_=False,
            ).label("isExternal")
        ).label("number_of_externalBookings")

    @hybrid_property
    def validated_incident_id(self) -> int | None:
        for booking_incident in self.incidents:
            if booking_incident.incident.status == finance_models.IncidentStatus.VALIDATED:
                return booking_incident.incident.id
        return None

    @validated_incident_id.expression  # type: ignore[no-redef]
    def validated_incident_id(cls) -> int | None:  # pylint: disable=no-self-argument
        return (
            sa.select(finance_models.FinanceIncident.id)
            .select_from(finance_models.FinanceIncident)
            .join(finance_models.BookingFinanceIncident)
            .where(
                sa.and_(
                    finance_models.BookingFinanceIncident.bookingId == Booking.id,
                    finance_models.FinanceIncident.status == finance_models.IncidentStatus.VALIDATED,
                )
            )
            .limit(1)
            .correlate(Booking)
            .scalar_subquery()
        )

    @property
    def reimbursement_pricing(self) -> finance_models.Pricing | None:
        """Return related pricing if this booking has been reimbursed."""
        pricings = [
            pricing
            for pricing in self.pricings
            if pricing.status
            in (
                finance_models.PricingStatus.PROCESSED,
                finance_models.PricingStatus.INVOICED,
            )
        ]

        pricings = sorted(pricings, key=lambda x: x.creationDate, reverse=True)
        if pricings:
            return pricings[0]

        return None

    @property
    def invoiced_pricing(self) -> finance_models.Pricing | None:
        pricings = [pricing for pricing in self.pricings if pricing.status == finance_models.PricingStatus.INVOICED]
        pricings = sorted(pricings, key=lambda pricing: pricing.creationDate, reverse=True)
        if pricings:
            return pricings[0]
        return None

    @property
    def cashflow_batch(self) -> finance_models.CashflowBatch | None:
        """Return cashflow batch in which this booking has been
        reimbursed (if any).
        """
        if not self.reimbursement_pricing:
            return None

        cashflow = self.reimbursement_pricing.cashflow
        if not cashflow:
            return None

        return cashflow.batch

    @property
    def reimbursement_rate(self) -> float | None:
        if not self.reimbursement_pricing:
            return None

        try:
            # pricing.amount is in cents, amount in euros
            # -> the result is a percentage
            return float("{:.2f}".format((-self.reimbursement_pricing.amount / self.total_amount)))
        except (decimal.DivisionByZero, decimal.InvalidOperation):  # raised when both values are 0
            return None

    @hybrid_property
    def display_even_if_used(self) -> bool:
        return (
            self.stock.offer.subcategoryId in offers_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES and self.amount == 0
        )

    @display_even_if_used.expression  # type: ignore[no-redef]
    def display_even_if_used(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(
            offers_models.Offer.subcategoryId.in_(offers_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES),
            cls.amount == 0,
        )

    @property
    def userReaction(self) -> ReactionTypeEnum | None:
        is_linked_to_product = self.stock.offer.product is not None

        if is_linked_to_product:
            return next(
                (
                    reaction.reactionType
                    for reaction in self.user.reactions
                    if reaction.productId == self.stock.offer.productId
                ),
                None,
            )
        return next(
            (reaction.reactionType for reaction in self.user.reactions if reaction.offerId == self.stock.offerId), None
        )

    @property
    def enable_pop_up_reaction(self) -> bool:
        if self.dateUsed:
            cooldown_datetime = get_cooldown_datetime_by_subcategories(self.stock.offer.subcategoryId)
            return (
                self.dateUsed <= cooldown_datetime
                and self.stock.offer.subcategoryId in SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE
                and self.userReaction is None
            )
        return False

    @property
    def can_react(self) -> bool:
        return self.dateUsed is not None and self.stock.offer.subcategoryId in SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE


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
            COALESCE(SUM(COALESCE(booking_finance_incident."newTotalAmount" / 100,
                            booking.amount * booking.quantity)), 0) INTO sum_bookings
        FROM
            booking
            LEFT OUTER JOIN booking_finance_incident ON booking_finance_incident."bookingId" = booking.id
            LEFT OUTER JOIN finance_incident ON  finance_incident.id = booking_finance_incident."incidentId" AND finance_incident."status" = '{finance_models.IncidentStatus.VALIDATED.value}'
        WHERE
            booking."depositId" = deposit_id
            AND NOT booking.status = '{BookingStatus.CANCELLED.value}'
            AND (NOT only_used_bookings OR booking.status IN ('{BookingStatus.USED.value}', '{BookingStatus.REIMBURSED.value}'));
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
            -- Check the wallet if we are changing the quantity or increasing the amount
            -- The backend should never do that, but let's be defensive.
            (NEW."quantity" != OLD."quantity" OR NEW."amount" > OLD."amount")
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
    FOR EACH ROW
    -- Happens only for USED to REIMBURSED transition
    WHEN (NEW.status <> '{BookingStatus.REIMBURSED.value}')
    EXECUTE PROCEDURE check_booking()
    """
sa.event.listen(Booking.__table__, "after_create", sa.DDL(Booking.trig_ddl))

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

sa.event.listen(Booking.__table__, "after_create", sa.DDL(Booking.trig_update_cancellationDate_on_isCancelled_ddl))


class FraudulentBookingTag(PcObject, Base, Model):
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    bookingId: int = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=False, unique=True)

    booking: sa_orm.Mapped["Booking"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], back_populates="fraudulentBookingTag"
    )

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    author: sa_orm.Mapped["users_models.User | None"] = sa_orm.relationship("User", foreign_keys=[authorId])
