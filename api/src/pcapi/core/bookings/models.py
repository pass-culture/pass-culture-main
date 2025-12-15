import decimal
import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.elements import Label
from sqlalchemy.sql.selectable import ScalarSelect

import pcapi.core.finance.models as finance_models
from pcapi.core.bookings import exceptions
from pcapi.core.bookings.constants import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.utils import SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE
from pcapi.core.bookings.utils import get_cooldown_datetime_by_subcategories
from pcapi.core.categories import subcategories
from pcapi.core.offers import models as offers_models
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.users import models as users_models
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils
from pcapi.utils.db import MagicEnum
from pcapi.utils.human_ids import humanize


if TYPE_CHECKING:
    from pcapi.core.achievements.models import Achievement
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


class BookingsListStatus(enum.Enum):
    ONGOING = "ongoing"
    ENDED = "ended"


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


class ExternalBooking(PcObject, Model):
    __tablename__ = "external_booking"
    bookingId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=False
    )

    booking: sa_orm.Mapped["Booking"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], back_populates="externalBookings"
    )

    barcode: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String, nullable=False)

    seat: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String, nullable=True)

    additional_information: sa_orm.Mapped[dict | None] = sa_orm.mapped_column(postgresql.JSONB, nullable=True)


class Booking(PcObject, Model):
    __tablename__ = "booking"

    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )

    dateUsed: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True, index=True)

    stockId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("stock.id"), index=True, nullable=False
    )

    stock: sa_orm.Mapped["offers_models.Stock"] = sa_orm.relationship(
        "Stock", foreign_keys=[stockId], back_populates="bookings"
    )

    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False
    )

    venue: sa_orm.Mapped["offerers_models.Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="bookings"
    )

    offererId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id"), index=True, nullable=False
    )

    offerer: sa_orm.Mapped["offerers_models.Offerer"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="bookings"
    )

    quantity: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False, default=1)

    token: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(6), unique=True, nullable=False)

    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False
    )
    user: sa_orm.Mapped["users_models.User"] = sa_orm.relationship(
        "User", foreign_keys=[userId], back_populates="userBookings"
    )

    activationCode: sa_orm.Mapped["offers_models.ActivationCode"] = sa_orm.relationship(
        "ActivationCode", foreign_keys="ActivationCode.bookingId", uselist=False, back_populates="booking"
    )

    amount: sa_orm.Mapped[Decimal] = sa_orm.mapped_column(sa.Numeric(10, 2), nullable=False)

    priceCategoryLabel: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    cancellationDate: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    displayAsEnded: sa_orm.Mapped[bool | None] = sa_orm.mapped_column(sa.Boolean, nullable=True)

    cancellationLimitDate: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    cancellationReason: sa_orm.Mapped[BookingCancellationReasons | None] = sa_orm.mapped_column(
        "cancellationReason",
        sa.Enum(
            BookingCancellationReasons,
            values_callable=lambda x: [reason.value for reason in BookingCancellationReasons],
        ),
        nullable=True,
    )

    externalBookings: sa_orm.Mapped[list[ExternalBooking]] = sa_orm.relationship(
        ExternalBooking, foreign_keys="ExternalBooking.bookingId", back_populates="booking"
    )

    cancellationUserId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), nullable=True
    )
    cancellationUser: sa_orm.Mapped["users_models.User | None"] = sa_orm.relationship(
        "User", foreign_keys=[cancellationUserId]
    )

    status: sa_orm.Mapped[BookingStatus] = sa_orm.mapped_column(
        sa.Enum(BookingStatus), nullable=False, default=BookingStatus.CONFIRMED
    )

    validationAuthorType: sa_orm.Mapped[BookingValidationAuthorType | None] = sa_orm.mapped_column(
        sa.Enum(BookingValidationAuthorType), nullable=True
    )

    reimbursementDate = sa_orm.mapped_column(sa.DateTime, nullable=True)

    depositId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("deposit.id"), index=True, nullable=True
    )

    deposit: sa_orm.Mapped["finance_models.Deposit | None"] = sa_orm.relationship(
        "Deposit", foreign_keys=[depositId], back_populates="bookings"
    )

    usedRecreditType: sa_orm.Mapped[BookingRecreditType | None] = sa_orm.mapped_column(
        MagicEnum(BookingRecreditType), nullable=True
    )

    fraudulentBookingTag: sa_orm.Mapped["FraudulentBookingTag | None"] = sa_orm.relationship(
        "FraudulentBookingTag", foreign_keys="FraudulentBookingTag.bookingId", back_populates="booking", uselist=False
    )

    achievements: sa_orm.Mapped[list["Achievement"]] = sa_orm.relationship(
        "Achievement", foreign_keys="Achievement.bookingId", back_populates="booking"
    )
    finance_events: sa_orm.Mapped[list["finance_models.FinanceEvent"]] = sa_orm.relationship(
        "FinanceEvent", foreign_keys="FinanceEvent.bookingId", back_populates="booking"
    )
    pricings: sa_orm.Mapped[list["finance_models.Pricing"]] = sa_orm.relationship(
        "Pricing", foreign_keys="Pricing.bookingId", back_populates="booking"
    )
    incidents: sa_orm.Mapped[list["finance_models.BookingFinanceIncident"]] = sa_orm.relationship(
        "BookingFinanceIncident", foreign_keys="BookingFinanceIncident.bookingId", back_populates="booking"
    )
    payments: sa_orm.Mapped[list["finance_models.Payment"]] = sa_orm.relationship(
        "Payment", foreign_keys="Payment.bookingId", back_populates="booking"
    )

    __table_args__ = (
        sa.Index("ix_booking_date_created", dateCreated),
        sa.Index("ix_booking_status", status),
        # Index avoids timeout when any user is deleted (because of foreign key)
        sa.Index("ix_booking_cancellationUserId", cancellationUserId, postgresql_where=cancellationUserId.is_not(None)),
        sa.Index(
            "ix_booking_cancellation_reason", cancellationReason, postgresql_where=cancellationReason.is_not(None)
        ),
    )

    def mark_as_used(self, validation_author_type: BookingValidationAuthorType) -> None:
        if self.is_used_or_reimbursed:
            raise exceptions.BookingHasAlreadyBeenUsed()
        if self.status is BookingStatus.CANCELLED:
            raise exceptions.BookingIsCancelled()
        self.dateUsed = date_utils.get_naive_utc_now()
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
        self.cancellationDate = date_utils.get_naive_utc_now()
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
        self.dateUsed = date_utils.get_naive_utc_now()

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
    def isArchivable(self) -> bool | None:
        return (
            self.stock.offer.subcategoryId in offers_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES
            and not self.stock.price
        ) or self.displayAsEnded

    @property
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

    @hybrid_property
    def isConfirmed(self) -> bool:
        return self.cancellationLimitDate is not None and self.cancellationLimitDate <= date_utils.get_naive_utc_now()

    @isConfirmed.inplace.expression
    @classmethod
    def _isConfirmedExpression(cls) -> ColumnElement[bool]:
        return sa.and_(cls.cancellationLimitDate.is_not(None), cls.cancellationLimitDate <= sa.func.now())

    @hybrid_property
    def is_used_or_reimbursed(self) -> bool:
        return self.status in [BookingStatus.USED, BookingStatus.REIMBURSED]

    @is_used_or_reimbursed.inplace.expression
    @classmethod
    def _is_used_or_reimbursed_expression(cls) -> ColumnElement[bool]:
        return cls.status.in_([BookingStatus.USED, BookingStatus.REIMBURSED])

    @hybrid_property
    def isReimbursed(self) -> bool:
        return self.status == BookingStatus.REIMBURSED

    @isReimbursed.inplace.expression
    @classmethod
    def _isReimbursedExpression(cls) -> ColumnElement[bool]:
        return cls.status == BookingStatus.REIMBURSED

    @hybrid_property
    def isCancelled(self) -> bool:
        return self.status == BookingStatus.CANCELLED

    @isCancelled.inplace.expression
    @classmethod
    def _isCancelledExpression(cls) -> ColumnElement[bool]:
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

    @isExternal.inplace.expression
    @classmethod
    def _isExternalExpression(cls) -> Label:
        return sa.select(
            sa.case(
                (sa.exists().where(ExternalBooking.bookingId == cls.id).correlate(cls), True),
                else_=False,
            ).label("isExternal")
        ).label("number_of_externalBookings")

    @hybrid_property
    def validated_incident_id(self) -> int | None:
        for booking_incident in self.incidents:
            if booking_incident.incident.status in (
                finance_models.IncidentStatus.VALIDATED,
                finance_models.IncidentStatus.INVOICED,
            ):
                return booking_incident.incident.id
        return None

    @validated_incident_id.inplace.expression
    @classmethod
    def _validated_incident_id_expression(cls) -> ScalarSelect:
        return (
            sa.select(finance_models.FinanceIncident.id)
            .select_from(finance_models.FinanceIncident)
            .join(finance_models.BookingFinanceIncident)
            .where(
                sa.and_(
                    finance_models.BookingFinanceIncident.bookingId == Booking.id,
                    finance_models.FinanceIncident.status.in_(
                        (finance_models.IncidentStatus.VALIDATED, finance_models.IncidentStatus.INVOICED)
                    ),
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

    @display_even_if_used.inplace.expression
    @classmethod
    def _display_even_if_used_expression(cls) -> ColumnElement[bool]:
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
        deposit_amount numeric := (SELECT CASE WHEN "expirationDate" > now() THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
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
            LEFT OUTER JOIN finance_incident ON finance_incident.id = booking_finance_incident."incidentId" AND finance_incident."status" IN ('{finance_models.IncidentStatus.VALIDATED.value}', '{finance_models.IncidentStatus.INVOICED.value}')
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


class FraudulentBookingTag(PcObject, Model):
    __tablename__ = "fraudulent_booking_tag"
    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )

    bookingId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=False, unique=True
    )

    booking: sa_orm.Mapped["Booking"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], back_populates="fraudulentBookingTag"
    )

    authorId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False
    )

    author: sa_orm.Mapped["users_models.User | None"] = sa_orm.relationship("User", foreign_keys=[authorId])
