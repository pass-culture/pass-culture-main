"""Finance-related models.

In all models of this package, amounts are in euro cents. They are
signed:
- a negative amount will be outgoing (payable by us to someone);
- a positive amount will be incoming (payable to us by someone).
"""

import dataclasses
import datetime
import decimal
import enum
import typing
from uuid import UUID

import psycopg2.extras
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_psql
import sqlalchemy.ext.mutable as sa_mutable
import sqlalchemy.orm as sa_orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.selectable import Exists

import pcapi.utils.db as db_utils
from pcapi import settings
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject

from . import utils


if typing.TYPE_CHECKING:
    import pcapi.core.bookings.models as bookings_models
    import pcapi.core.educational.models as educational_models
    import pcapi.core.offerers.models as offerers_models
    import pcapi.core.offers.models as offers_models
    import pcapi.core.users.models as users_models

    from . import conf


class DepositType(enum.Enum):
    GRANT_17_18 = "GRANT_17_18"
    GRANT_FREE = "GRANT_FREE"
    # legacy deposit types that are present in the database
    GRANT_15_17 = "GRANT_15_17"
    GRANT_18 = "GRANT_18"


class Deposit(PcObject, Base, Model):
    __tablename__ = "deposit"
    amount: decimal.Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    user: sa_orm.Mapped["users_models.User"] = sa_orm.relationship("User", foreign_keys=[userId], backref="deposits")

    bookings: sa_orm.Mapped[list["bookings_models.Booking"]] = sa_orm.relationship("Booking", back_populates="deposit")

    source: str = sa.Column(sa.String(300), nullable=False)

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    dateUpdated = sa.Column(sa.DateTime, nullable=True, onupdate=sa.func.now())

    expirationDate = sa.Column(sa.DateTime, nullable=True)

    version: int = sa.Column(sa.SmallInteger, nullable=False)

    type: DepositType = sa.Column(
        sa.Enum(DepositType, native_enum=False, create_constraint=False),
        nullable=False,
        server_default=DepositType.GRANT_18.value,
    )

    recredits: sa_orm.Mapped[list["Recredit"]] = sa_orm.relationship(
        "Recredit", order_by="Recredit.dateCreated.desc()", back_populates="deposit"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "type",
            name="unique_type_per_user",
        ),
    )

    @property
    def specific_caps(self) -> "conf.SpecificCaps":
        from . import conf

        physical_cap = None
        digital_cap = None

        if self.type == DepositType.GRANT_15_17:
            return conf.SpecificCaps(digital_cap=digital_cap, physical_cap=physical_cap)

        if self.type == DepositType.GRANT_18:
            if self.version == 1:
                physical_cap = conf.GRANT_18_PHYSICAL_CAP_V1
                digital_cap = conf.GRANT_18_DIGITAL_CAP_V1
            elif self.version == 2:
                physical_cap = conf.GRANT_18_PHYSICAL_CAP_V2
                digital_cap = conf.GRANT_18_DIGITAL_CAP_V2

        if self.type == DepositType.GRANT_17_18:
            physical_cap = conf.GRANT_17_18_PHYSICAL_CAP
            digital_cap = conf.GRANT_17_18_DIGITAL_CAP

        if self.user.departementCode in conf.SPECIFIC_DIGITAL_CAPS_BY_DEPARTMENT_CODE:
            digital_cap = conf.SPECIFIC_DIGITAL_CAPS_BY_DEPARTMENT_CODE[self.user.departementCode]

        return conf.SpecificCaps(digital_cap=digital_cap, physical_cap=physical_cap)


@dataclasses.dataclass
class GrantedDeposit:
    amount: decimal.Decimal
    expiration_date: datetime.datetime
    type: DepositType
    version: int = 1


class RecreditType(enum.Enum):
    RECREDIT_15 = "Recredit15"
    RECREDIT_16 = "Recredit16"
    RECREDIT_17 = "Recredit17"
    RECREDIT_18 = "Recredit18"
    MANUAL_MODIFICATION = "ManualModification"
    PREVIOUS_DEPOSIT = "PreviousDeposit"
    FINANCE_INCIDENT_RECREDIT = "FinanceIncidentRecredit"


class Recredit(PcObject, Base, Model):
    __tablename__ = "recredit"
    depositId: int = sa.Column(sa.BigInteger, sa.ForeignKey("deposit.id"), nullable=False)

    deposit: sa_orm.Mapped[Deposit] = sa_orm.relationship(
        "Deposit", foreign_keys=[depositId], back_populates="recredits"
    )

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    amount: decimal.Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)

    recreditType: RecreditType = sa.Column(
        sa.Enum(RecreditType, native_enum=False, create_constraint=False),
        nullable=False,
    )

    comment = sa.Column(sa.Text, nullable=True)


class FinanceEventStatus(enum.Enum):
    PENDING = "pending"  # related booking does not have any pricing point
    READY = "ready"  # has a pricing point, is ready to be priced
    PRICED = "priced"
    CANCELLED = "cancelled"  # related booking has been used and then cancelled
    NOT_TO_BE_PRICED = "not to be priced"  # will not be priced


CANCELLABLE_FINANCE_EVENT_STATUSES = {
    FinanceEventStatus.PENDING,
    FinanceEventStatus.READY,
    FinanceEventStatus.PRICED,
}


class FinanceEventMotive(enum.Enum):
    BOOKING_USED = "booking-used"
    BOOKING_USED_AFTER_CANCELLATION = "booking-used-after-cancellation"
    BOOKING_UNUSED = "booking-unused"
    BOOKING_CANCELLED_AFTER_USE = "booking-cancelled-after-use"
    INCIDENT_REVERSAL_OF_ORIGINAL_EVENT = "incident-reversal-of-original-event"
    INCIDENT_NEW_PRICE = "incident-new-price"
    INCIDENT_COMMERCIAL_GESTURE = "incident-commercial-gesture"


class PricingStatus(enum.Enum):
    CANCELLED = "cancelled"
    VALIDATED = "validated"  # will be taken in account in next cashflow
    PROCESSED = "processed"  # has an associated cashflow
    INVOICED = "invoiced"  # has an associated invoice (whose cashflows are "accepted")


DELETABLE_PRICING_STATUSES = {PricingStatus.VALIDATED, PricingStatus.CANCELLED}


class PricingLineCategory(enum.Enum):
    OFFERER_REVENUE = "offerer revenue"
    OFFERER_CONTRIBUTION = "offerer contribution"
    PASS_CULTURE_COMMISSION = "pass culture commission"
    COMMERCIAL_GESTURE = "commercial gesture"


class PricingLogReason(enum.Enum):
    MARK_AS_UNUSED = "mark as unused"
    CHANGE_AMOUNT = "change amount"
    CHANGE_DATE = "change date"
    GENERATE_CASHFLOW = "generate cashflow"
    GENERATE_INVOICE = "generate invoice"


class Frequency(enum.Enum):
    EVERY_TWO_WEEKS = "every two weeks"


class CashflowStatus(enum.Enum):
    # A cashflow starts by being pending, i.e. it's waiting for being
    # sent to our accounting system.
    PENDING = "pending"
    # Then it is sent to our accounting system for review.
    UNDER_REVIEW = "under review"
    # Intermediary status to await acceptance from finance tool (after invoice push)
    PENDING_ACCEPTANCE = "pending acceptance"
    # And it's finally sent to the bank. By default, we decide it's
    # accepted. The bank will inform us later if it rejected the
    # cashflow. (For now, this happens outside of this application,
    # which is why there is no "rejected" status below for now.)
    ACCEPTED = "accepted"


class BankAccountApplicationStatus(enum.Enum):
    DRAFT = "en_construction"
    ON_GOING = "en_instruction"
    ACCEPTED = "accepte"
    REFUSED = "refuse"
    WITHOUT_CONTINUATION = "sans_suite"
    WITH_PENDING_CORRECTIONS = "a_corriger"


class BankAccount(PcObject, Base, Model, DeactivableMixin):
    __tablename__ = "bank_account"
    label: str = sa.Column(sa.String(100), nullable=False)
    offererId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    offerer: sa_orm.Mapped["offerers_models.Offerer"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="bankAccounts"
    )
    iban: str = sa.Column(sa.String(27), nullable=False)
    bic: str = sa.Column(sa.String(11), nullable=False)
    dsApplicationId: int | None = sa.Column(sa.BigInteger, nullable=True, unique=True)
    status: sa_orm.Mapped[BankAccountApplicationStatus] = sa.Column(
        sa.Enum(BankAccountApplicationStatus), nullable=False
    )
    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    dateLastStatusUpdate: datetime.datetime = sa.Column(sa.DateTime)
    venueLinks: sa_orm.Mapped[list["offerers_models.VenueBankAccountLink"]] = sa_orm.relationship(
        "VenueBankAccountLink", back_populates="bankAccount", passive_deletes=True
    )
    statusHistory: sa_orm.Mapped[list["BankAccountStatusHistory"]] = sa_orm.relationship(
        "BankAccountStatusHistory",
        back_populates="bankAccount",
        foreign_keys="BankAccountStatusHistory.bankAccountId",
        uselist=True,
    )
    lastCegidSyncDate = sa.Column(sa.DateTime, nullable=True)

    @property
    def current_link(self) -> "offerers_models.VenueBankAccountLink | None":
        for link in self.venueLinks:
            if link.timespan.upper is None and link.timespan.lower <= datetime.datetime.utcnow():
                return link
        return None


class BankAccountStatusHistory(PcObject, Base, Model):
    __tablename__ = "bank_account_status_history"
    bankAccountId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("bank_account.id", ondelete="CASCADE"), index=True, nullable=False
    )
    bankAccount: sa_orm.Mapped[BankAccount] = sa_orm.relationship(
        BankAccount, foreign_keys=[bankAccountId], back_populates="statusHistory"
    )
    status: BankAccountApplicationStatus = sa.Column(sa.Enum(BankAccountApplicationStatus), nullable=False)
    timespan: psycopg2.extras.DateTimeRange = sa.Column(sa_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # One status at a time per bank account.
        sa_psql.ExcludeConstraint(("bankAccountId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class FinanceEvent(PcObject, Base, Model):
    __tablename__ = "finance_event"
    creationDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    # In most cases, `valueDate` is `Booking.dateUsed` but it's useful
    # to denormalize it here: many queries use this column and we thus
    # avoid a JOIN.
    valueDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False)
    # The date that is used to price events in a determined, stable order.
    pricingOrderingDate: datetime.datetime | None = sa.Column(sa.DateTime, nullable=True)

    status: FinanceEventStatus = sa.Column(db_utils.MagicEnum(FinanceEventStatus), index=True, nullable=False)
    motive: FinanceEventMotive = sa.Column(db_utils.MagicEnum(FinanceEventMotive), nullable=False)

    bookingId = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=True)
    booking: sa_orm.Mapped["bookings_models.Booking | None"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], backref="finance_events"
    )
    collectiveBookingId = sa.Column(sa.BigInteger, sa.ForeignKey("collective_booking.id"), index=True, nullable=True)
    collectiveBooking: sa_orm.Mapped["educational_models.CollectiveBooking | None"] = sa_orm.relationship(
        "CollectiveBooking", foreign_keys=[collectiveBookingId], backref="finance_events"
    )
    bookingFinanceIncidentId = sa.Column(
        sa.BigInteger, sa.ForeignKey("booking_finance_incident.id"), index=True, nullable=True
    )
    bookingFinanceIncident: sa_orm.Mapped["BookingFinanceIncident | None"] = sa_orm.relationship(
        "BookingFinanceIncident", foreign_keys=[bookingFinanceIncidentId], backref="finance_events"
    )

    # `venueId` is denormalized and comes from `booking.venueId`
    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=True)
    venue: sa_orm.Mapped["offerers_models.Venue | None"] = sa_orm.relationship("Venue", foreign_keys=[venueId])
    # `pricingPointId` may be None if the related venue did not have
    # any pricing point when the finance event occurred. If so, it
    # will be populated later from `link_venue_to_pricing_point()`.
    pricingPointId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=True)
    pricingPoint: sa_orm.Mapped["offerers_models.Venue | None"] = sa_orm.relationship(
        "Venue", foreign_keys=[pricingPointId]
    )

    __table_args__ = (
        # An event relates to an individual or a collective booking, never both.
        sa.CheckConstraint('num_nonnulls("bookingId", "collectiveBookingId", "bookingFinanceIncidentId") = 1'),
        # There cannot be two pending or ready events for the same individual booking.
        sa.Index(
            "idx_uniq_individual_booking_id",
            bookingId,
            postgresql_where=status.in_((FinanceEventStatus.PENDING, FinanceEventStatus.READY)),
            unique=True,
        ),
        # Ditto for collective bookings.
        sa.Index(
            "idx_uniq_collective_booking_id",
            collectiveBookingId,
            postgresql_where=status.in_((FinanceEventStatus.PENDING, FinanceEventStatus.READY)),
            unique=True,
        ),
        # Ditto for booking finance incidents.
        sa.Index(
            "idx_uniq_booking_finance_incident_id",
            bookingFinanceIncidentId,
            motive,
            postgresql_where=status.in_((FinanceEventStatus.PENDING, FinanceEventStatus.READY)),
            unique=True,
        ),
        # Check status / pricingPointId / pricingOrderingDate consistency.
        sa.CheckConstraint(
            """
            (
              status = 'pending'
              AND "pricingPointId" IS NULL
              AND "pricingOrderingDate" IS NULL
            ) OR (
              "pricingPointId" IS NOT NULL
              AND "pricingOrderingDate" IS NOT NULL
            )
            OR status in ('cancelled', 'not to be priced')
            """,
            name="status_pricing_point_ordering_date_check",
        ),
    )


class CashflowPricing(Base, Model):
    """An association table between cashflows and pricings for their
    many-to-many relationship.

    A cashflow is "naturally" linked to multiple pricings of the same
    pricing point: we build a cashflow based on all pricings of a
    given period (e.g. two weeks).

    A pricing may also be linked to multiple cashflows: for example,
    if a cashflow is rejected by the bank because the bank information
    are wrong, we will create another cashflow and the pricing will
    thus be linked to two cashflows.
    """

    __tablename__ = "cashflow_pricing"
    cashflowId: int = sa.Column(sa.BigInteger, sa.ForeignKey("cashflow.id"), index=True, primary_key=True)
    pricingId: int = sa.Column(sa.BigInteger, sa.ForeignKey("pricing.id"), index=True, primary_key=True)


class Pricing(PcObject, Base, Model):
    __tablename__ = "pricing"
    status: PricingStatus = sa.Column(db_utils.MagicEnum(PricingStatus), index=True, nullable=False)

    bookingId = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=True)
    booking: sa_orm.Mapped["bookings_models.Booking | None"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], backref="pricings"
    )
    collectiveBookingId = sa.Column(sa.BigInteger, sa.ForeignKey("collective_booking.id"), index=True, nullable=True)
    collectiveBooking: sa_orm.Mapped["educational_models.CollectiveBooking | None"] = sa_orm.relationship(
        "CollectiveBooking", foreign_keys=[collectiveBookingId], backref="pricings"
    )
    eventId = sa.Column(sa.BigInteger, sa.ForeignKey("finance_event.id"), index=True, nullable=False)
    event: sa_orm.Mapped[FinanceEvent] = sa_orm.relationship("FinanceEvent", foreign_keys=[eventId], backref="pricings")

    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)
    venue: sa_orm.Mapped["offerers_models.Venue"] = sa_orm.relationship("Venue", foreign_keys=[venueId])

    pricingPointId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), index=True, nullable=False)
    pricingPoint: sa_orm.Mapped["offerers_models.Venue"] = sa_orm.relationship("Venue", foreign_keys=[pricingPointId])

    creationDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    # `valueDate` is `Booking.dateUsed` but it's useful to denormalize
    # it here: many queries use this column and we thus avoid a JOIN.
    valueDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False)

    # See the note about `amount` at the beginning of this module.
    # The amount is zero for bookings that are not reimbursable. We do
    # create 0-pricings for these bookings to avoid processing them
    # again and again.
    amount: int = sa.Column(sa.Integer, nullable=False)
    # See constraints below about the relationship between rate,
    # standardRule and customRuleId.
    standardRule: str = sa.Column(sa.Text, nullable=False)
    customRuleId = sa.Column(sa.BigInteger, sa.ForeignKey("custom_reimbursement_rule.id"), index=True, nullable=True)
    customRule: sa_orm.Mapped["CustomReimbursementRule | None"] = sa_orm.relationship(
        "CustomReimbursementRule", foreign_keys=[customRuleId]
    )

    # Revenue is in euro cents. It's the revenue of the pricing point
    # as of `pricing.valueDate` (thus including the related booking).
    # It is zero or positive.
    revenue: int = sa.Column(sa.Integer, nullable=False)

    cashflows: sa_orm.Mapped[list["Cashflow"]] = sa_orm.relationship(
        "Cashflow", secondary=CashflowPricing.__table__, back_populates="pricings"
    )
    lines: sa_orm.Mapped[list["PricingLine"]] = sa_orm.relationship(
        "PricingLine", back_populates="pricing", order_by="PricingLine.id"
    )
    logs: sa_orm.Mapped[list["PricingLog"]] = sa_orm.relationship(
        "PricingLog", back_populates="pricing", order_by="PricingLog.timestamp"
    )

    __table_args__ = (
        sa.Index("idx_uniq_booking_id", bookingId, postgresql_where=status != PricingStatus.CANCELLED, unique=True),
        sa.CheckConstraint(
            """
            (
              "standardRule" = ''
              AND "customRuleId" IS NOT NULL
            ) OR (
              "standardRule" != ''
              AND "customRuleId" IS NULL
            )
            """,
            name="reimbursement_rule_constraint_check",
        ),
    )

    @property
    def cashflow(self) -> "Cashflow | None":
        """
        The Pricing-Cashflow relation is implemented as a
        many-to-many one but for now a Pricing can only have one
        cashflow.
        """
        if not self.cashflows:
            return None

        return self.cashflows[0]

    @hybrid_property
    def xpf_amount(self) -> int:
        return utils.euros_to_xpf(self.amount)

    @xpf_amount.expression  # type: ignore[no-redef]
    def xpf_amount(cls) -> int:
        return sa.cast(sa.func.round(cls.amount * utils.EUR_TO_XPF_RATE), sa.Integer)


class PricingLine(PcObject, Base, Model):
    __tablename__ = "pricing_line"
    pricingId = sa.Column(sa.BigInteger, sa.ForeignKey("pricing.id"), index=True, nullable=True)
    pricing: sa_orm.Mapped[Pricing] = sa_orm.relationship("Pricing", foreign_keys=[pricingId], back_populates="lines")

    # See the note about `amount` at the beginning of this module.
    amount: int = sa.Column(sa.Integer, nullable=False)

    category: PricingLineCategory = sa.Column(db_utils.MagicEnum(PricingLineCategory), nullable=False)


class PricingLog(PcObject, Base, Model):
    """A pricing log is created whenever the status of a pricing
    changes.
    """

    __tablename__ = "pricing_log"
    pricingId: int = sa.Column(sa.BigInteger, sa.ForeignKey("pricing.id"), index=True, nullable=False)
    pricing: sa_orm.Mapped[Pricing] = sa_orm.relationship("Pricing", foreign_keys=[pricingId], back_populates="logs")

    timestamp: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    statusBefore: PricingStatus = sa.Column(db_utils.MagicEnum(PricingStatus), nullable=False)
    statusAfter: PricingStatus = sa.Column(db_utils.MagicEnum(PricingStatus), nullable=False)
    reason: PricingLogReason = sa.Column(db_utils.MagicEnum(PricingLogReason), nullable=False)


# TODO(fseguin|dbaty, 2022-01-11): maybe merge with core.categories.subcategories.ReimbursementRuleChoices ?
class RuleGroup(enum.Enum):
    STANDARD = dict(
        label="Barème général",
        position=1,
    )
    BOOK = dict(
        label="Barème livres",
        position=2,
    )
    NOT_REIMBURSED = dict(
        label="Barème non remboursé",
        position=3,
    )
    CUSTOM = dict(
        label="Barème dérogatoire",
        position=4,
    )
    DEPRECATED = dict(
        label="Barème désuet",
        position=5,
    )


class ReimbursementRule:
    valid_from: datetime.datetime | None = None
    valid_until: datetime.datetime | None = None
    # A `rate` attribute (or property) must be defined by subclasses.
    # It's not defined in this abstract class because SQLAlchemy would
    # then miss the `rate` column in `CustomReimbursementRule`.

    def is_active(self, booking: "bookings_models.Booking") -> bool:
        if booking.dateUsed is None:
            raise ValueError("Can't compare None to datetime")
        valid_from = self.valid_from or datetime.datetime(datetime.MINYEAR, 1, 1)
        valid_until = self.valid_until or datetime.datetime(datetime.MAXYEAR, 1, 1)
        return valid_from <= booking.dateUsed < valid_until

    def is_relevant(
        self,
        booking: "bookings_models.Booking",
        cumulative_revenue: int,
    ) -> bool:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        raise NotImplementedError()

    def matches(self, booking: "bookings_models.Booking", cumulative_revenue: int) -> bool:
        return self.is_active(booking) and self.is_relevant(booking, cumulative_revenue)

    def apply(
        self,
        booking: "bookings_models.Booking",
        custom_total_amount: int | None = None,
    ) -> int:
        base = custom_total_amount or utils.to_cents(booking.total_amount)
        return utils.round_to_integer(base * self.rate)  # type: ignore[attr-defined]

    @property
    def group(self) -> RuleGroup:
        raise NotImplementedError()


class CustomReimbursementRule(PcObject, ReimbursementRule, Base, Model):
    """Some offers are linked to custom reimbursement rules that overrides
    standard reimbursement rules.

    An offer may be linked to more than one reimbursement rules, but
    only one rule can be valid at a time.
    """

    __tablename__ = "custom_reimbursement_rule"

    offerId = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), nullable=True)

    offer: sa_orm.Mapped["offers_models.Offer | None"] = sa_orm.relationship(
        "Offer", foreign_keys=[offerId], backref="custom_reimbursement_rules"
    )

    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=True)

    venue: sa_orm.Mapped["offerers_models.Venue | None"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], backref="custom_reimbursement_rules"
    )

    offererId = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), nullable=True)

    offerer: sa_orm.Mapped["offerers_models.Offerer | None"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], backref="custom_reimbursement_rules"
    )

    # A list of identifiers of subcategories on which the rule applies.
    # If the list is empty, the rule applies on all offers of an
    # offerer.
    subcategories: list[str] = sa.Column(sa_psql.ARRAY(sa.Text()), server_default="{}")

    # The amount of the reimbursement, or NULL if `rate` is set.
    amount: int = sa.Column(sa.Integer, nullable=True)
    # rate is between 0 and 1 (included), or NULL if `amount` is set.
    rate: decimal.Decimal = sa.Column(sa.Numeric(5, 4), nullable=True)

    # timespan is an interval during which this rule is applicable
    # (see `is_active()` below). The lower bound is inclusive and
    # required. The upper bound is exclusive and optional. If there is
    # no upper bound, it means that the rule is still applicable.
    timespan: psycopg2.extras.DateTimeRange = sa.Column(sa_psql.TSRANGE)

    __table_args__ = (
        # A rule relates to an offer, a venue, or an offerer, never more than one.
        sa.CheckConstraint('num_nonnulls("offerId", "venueId", "offererId") = 1'),
        # A rule has an amount or a rate, never both.
        sa.CheckConstraint("num_nonnulls(amount, rate) = 1"),
        # A timespan must have a lower bound. Upper bound is optional.
        # Overlapping rules are rejected by `validation._check_reimbursement_rule_conflicts()`.
        sa.CheckConstraint("lower(timespan) IS NOT NULL"),
        sa.CheckConstraint("rate IS NULL OR (rate BETWEEN 0 AND 1)"),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)

    def is_active(self, booking: "bookings_models.Booking") -> bool:
        if booking.dateUsed < self.timespan.lower:
            return False
        return self.timespan.upper is None or booking.dateUsed < self.timespan.upper

    def is_relevant(
        self,
        booking: "bookings_models.Booking",
        cumulative_revenue: int = 0,  # unused
    ) -> bool:
        from pcapi.core.finance.api import get_pricing_point_link

        if booking.stock.offerId == self.offerId:
            return True
        if self.subcategories:
            if booking.stock.offer.subcategoryId not in self.subcategories:
                return False
        if get_pricing_point_link(booking).pricingPointId == self.venueId:
            return True
        if booking.offererId == self.offererId:
            return True
        return False

    def apply(
        self,
        booking: "bookings_models.Booking",
        custom_total_amount: int | None = None,
    ) -> int:
        if self.amount is not None:
            return booking.quantity * self.amount
        return super().apply(booking, custom_total_amount)

    @property
    def description(self) -> str:
        raise TypeError("A custom reimbursement rule does not have any description")

    @property
    def group(self) -> RuleGroup:
        return RuleGroup.CUSTOM


CustomReimbursementRule.trig_ddl = """
    CREATE OR REPLACE FUNCTION check_venue_has_siret()
    RETURNS TRIGGER AS $$
    BEGIN
      IF
       NOT NEW.venueId IS NULL
       AND
        (
         (
          SELECT venue.siret
          FROM venue
          WHERE "id"=NEW.venueId
         ) IS NULL
        )
      THEN
       RAISE EXCEPTION 'venueHasNoSiret'
       USING HINT = 'the venue must have a siret';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS check_venue_has_siret ON "custom_reimbursement_rule";
    CREATE TRIGGER check_venue_has_siret
    AFTER INSERT OR UPDATE ON custom_reimbursement_rule
    FOR EACH ROW
    EXECUTE PROCEDURE check_venue_has_siret()
    """

sa.event.listen(CustomReimbursementRule.__table__, "after_create", sa.DDL(CustomReimbursementRule.trig_ddl))


class InvoiceCashflow(Base, Model):
    """An association table between invoices and cashflows for their many-to-many relationship."""

    __tablename__ = "invoice_cashflow"
    invoiceId: int = sa.Column(sa.BigInteger, sa.ForeignKey("invoice.id"), index=True, primary_key=True)
    cashflowId: int = sa.Column(sa.BigInteger, sa.ForeignKey("cashflow.id"), index=True, primary_key=True)

    __table_args__ = (
        sa.PrimaryKeyConstraint(
            "invoiceId",
            "cashflowId",
            name="unique_invoice_cashflow_association",
        ),
    )


class Cashflow(PcObject, Base, Model):
    """A cashflow represents a specific amount money that is transferred
    between us and a third party. It may be outgoing or incoming.

    Cashflows with zero amount are there to enable generating invoices lines with 100% offerer contribution
    """

    __tablename__ = "cashflow"
    creationDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    status: CashflowStatus = sa.Column(db_utils.MagicEnum(CashflowStatus), index=True, nullable=False)

    bankAccountId: int = sa.Column(
        "bankAccountId", sa.BigInteger, sa.ForeignKey("bank_account.id"), index=True, nullable=True
    )
    bankAccount: sa_orm.Mapped[BankAccount] = sa_orm.relationship(BankAccount, foreign_keys=[bankAccountId])

    batchId: int = sa.Column(sa.BigInteger, sa.ForeignKey("cashflow_batch.id"), index=True, nullable=False)
    batch: sa_orm.Mapped["CashflowBatch"] = sa_orm.relationship(
        "CashflowBatch", foreign_keys=[batchId], backref="cashflows"
    )

    # See the note about `amount` at the beginning of this module.
    # The amount cannot be zero.
    # For now, only negative (outgoing) cashflows are automatically
    # generated. Positive (incoming) cashflows are manually created.
    amount: int = sa.Column(sa.Integer, nullable=False)

    logs: sa_orm.Mapped[list["CashflowLog"]] = sa_orm.relationship(
        "CashflowLog", back_populates="cashflow", order_by="CashflowLog.timestamp"
    )
    pricings: sa_orm.Mapped[list[Pricing]] = sa_orm.relationship(
        "Pricing", secondary=CashflowPricing.__table__, back_populates="cashflows"
    )
    invoices: sa_orm.Mapped[list["Invoice"]] = sa_orm.relationship(
        "Invoice", secondary=InvoiceCashflow.__table__, back_populates="cashflows"
    )


class CashflowLog(PcObject, Base, Model):
    """A cashflow log is created whenever the status of a cashflow
    changes.
    """

    __tablename__ = "cashflow_log"
    cashflowId: int = sa.Column(sa.BigInteger, sa.ForeignKey("cashflow.id"), index=True, nullable=False)
    cashflow: sa_orm.Mapped[Cashflow] = sa_orm.relationship(
        "Cashflow", foreign_keys=[cashflowId], back_populates="logs"
    )
    timestamp: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    statusBefore: CashflowStatus = sa.Column(db_utils.MagicEnum(CashflowStatus), nullable=False)
    statusAfter: CashflowStatus = sa.Column(db_utils.MagicEnum(CashflowStatus), nullable=False)
    details: dict | None = sa.Column(
        sa_mutable.MutableDict.as_mutable(sa_psql.JSONB), nullable=True, default={}, server_default="{}"
    )


class CashflowBatch(PcObject, Base, Model):
    """A cashflow batch groups cashflows that are sent to the bank at the
    same time (in a single file).
    """

    __tablename__ = "cashflow_batch"
    creationDate: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    cutoff: datetime.datetime = sa.Column(sa.DateTime, nullable=False, unique=True)
    label: str = sa.Column(sa.Text, nullable=False, unique=True)


class InvoiceLine(PcObject, Base, Model):
    __tablename__ = "invoice_line"
    invoiceId: int = sa.Column(sa.BigInteger, sa.ForeignKey("invoice.id"), index=True, nullable=False)
    invoice: sa_orm.Mapped["Invoice"] = sa_orm.relationship("Invoice", foreign_keys=[invoiceId], back_populates="lines")
    label: str = sa.Column(sa.Text, nullable=False)
    # a group is a dict of label and position, as defined in ..conf.InvoiceLineGroup
    group: dict = sa.Column(sa_psql.JSONB, nullable=False)
    contributionAmount: int = sa.Column(sa.Integer, nullable=False)
    reimbursedAmount: int = sa.Column(sa.Integer, nullable=False)
    rate: decimal.Decimal = sa.Column(
        sa.Numeric(5, 4, asdecimal=True),
        nullable=False,
    )

    @property
    def bookings_amount(self) -> int | None:
        """returns the (positive) raw amount of the used Bookings priced in this line"""
        if self.contributionAmount is None or self.reimbursedAmount is None:
            return None
        return self.contributionAmount - self.reimbursedAmount

    @property
    def contribution_rate(self) -> decimal.Decimal:
        return 1 - self.rate


class InvoiceStatus(enum.Enum):
    PENDING = "pending"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    REJECTED = "rejected"


@dataclasses.dataclass
class InvoiceLineGroup:
    position: int
    label: str
    lines: list[InvoiceLine]
    used_bookings_subtotal: float
    contribution_subtotal: float
    reimbursed_amount_subtotal: float


class Invoice(PcObject, Base, Model):
    """An invoice is linked to one or more cashflows and shows a summary
    of their related pricings.
    """

    __tablename__ = "invoice"
    date: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    reference: str = sa.Column(sa.Text, nullable=False, unique=True)
    bankAccountId = sa.Column(sa.BigInteger, sa.ForeignKey("bank_account.id"), index=True, nullable=True)
    bankAccount: sa_orm.Mapped[BankAccount] = sa_orm.relationship("BankAccount", foreign_keys=[bankAccountId])
    # See the note about `amount` at the beginning of this module.
    amount: int = sa.Column(sa.Integer, nullable=False)
    token: str = sa.Column(sa.Text, unique=True, nullable=False)
    lines: sa_orm.Mapped[list[InvoiceLine]] = sa_orm.relationship("InvoiceLine", back_populates="invoice")
    cashflows: sa_orm.Mapped[list[Cashflow]] = sa_orm.relationship(
        "Cashflow", secondary=InvoiceCashflow.__table__, back_populates="invoices"
    )
    status: InvoiceStatus = sa.Column(db_utils.MagicEnum(InvoiceStatus), nullable=False)

    @property
    def storage_object_id(self) -> str:
        if not self.date:  # can be None if the invoice is not yet saved
            raise ValueError("Invoice date is not set")
        return (
            f"{self.token}/{self.date.strftime('%d%m%Y')}-{self.reference}-"
            f"Justificatif-de-remboursement-pass-Culture.pdf"
        )

    @property
    def url(self) -> str:
        return f"{settings.OBJECT_STORAGE_URL}/invoices/{self.storage_object_id}"


# "Payment", "PaymentStatus" and "PaymentMessage" are deprecated. They
# were used in the "old" reimbursement system. No new data is created
# with these models since 2022-01-01. These models have been replaced
# by `Pricing`, `Cashflow` and other models listed above.
class Payment(PcObject, Base, Model):
    __tablename__ = "payment"
    bookingId = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=True)
    booking: sa_orm.Mapped["bookings_models.Booking"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], backref="payments"
    )
    collectiveBookingId = sa.Column(sa.BigInteger, sa.ForeignKey("collective_booking.id"), index=True, nullable=True)
    collectiveBooking: sa_orm.Mapped["educational_models.CollectiveBooking"] = sa_orm.relationship(
        "CollectiveBooking",
        foreign_keys=[collectiveBookingId],
        backref="payments",
    )
    # Contrary to other models, this amount is in euros, not eurocents.
    amount: decimal.Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)
    reimbursementRule = sa.Column(sa.String(200))
    reimbursementRate = sa.Column(sa.Numeric(10, 2))
    customReimbursementRuleId = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("custom_reimbursement_rule.id"),
    )
    customReimbursementRule: sa_orm.Mapped[CustomReimbursementRule | None] = sa_orm.relationship(
        "CustomReimbursementRule", foreign_keys=[customReimbursementRuleId], backref="payments"
    )
    recipientName: str = sa.Column(sa.String(140), nullable=False)
    recipientSiren: str = sa.Column(sa.String(9), nullable=False)
    iban = sa.Column(sa.String(27), nullable=True)
    bic = sa.Column(
        sa.String(11),
        sa.CheckConstraint(
            "(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)",
            name="check_iban_and_bic_xor_not_iban_and_not_bic",
        ),
        nullable=True,
    )
    comment = sa.Column(sa.Text, nullable=True)
    author: str = sa.Column(sa.String(27), nullable=False)
    transactionEndToEndId: UUID = sa.Column(sa_psql.UUID(as_uuid=True), nullable=True)
    transactionLabel = sa.Column(sa.String(140), nullable=True)
    paymentMessageId = sa.Column(sa.BigInteger, sa.ForeignKey("payment_message.id"), nullable=True)
    paymentMessage: sa_orm.Mapped["PaymentMessage"] = sa_orm.relationship(
        "PaymentMessage", foreign_keys=[paymentMessageId], backref=sa_orm.backref("payments")
    )
    batchDate = sa.Column(sa.DateTime, nullable=True, index=True)

    __table_args__ = (
        sa.CheckConstraint(
            """
            (
              "reimbursementRule" IS NOT NULL
              AND "reimbursementRate" IS NOT NULL
              AND "customReimbursementRuleId" IS NULL
            ) OR (
              "reimbursementRule" IS NULL
              AND "customReimbursementRuleId" IS NOT NULL
            )
            """,
            name="reimbursement_constraint_check",
        ),
    )


# `TransactionStatus` is deprecated. See comment above `Payment` model
# for further details.
class TransactionStatus(enum.Enum):
    PENDING = "PENDING"
    NOT_PROCESSABLE = "NOT PROCESSABLE"
    SENT = "SENT"
    ERROR = "ERROR"
    RETRY = "RETRY"
    BANNED = "BANNED"
    UNDER_REVIEW = "UNDER REVIEW"


# `PaymentStatus` is deprecated. See comment above `Payment` model for
# further details.
class PaymentStatus(PcObject, Base, Model):
    __tablename__ = "payment_status"
    paymentId: int = sa.Column(sa.BigInteger, sa.ForeignKey("payment.id"), index=True, nullable=False)
    payment: sa_orm.Mapped[Payment] = sa_orm.relationship("Payment", foreign_keys=[paymentId], backref="statuses")
    date: datetime.datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sa.func.now()
    )
    status: TransactionStatus = sa.Column(sa.Enum(TransactionStatus), nullable=False)
    detail = sa.Column(sa.VARCHAR(), nullable=True)


# `PaymentMessage` is deprecated. See comment above `Payment` model
# for further details.
class PaymentMessage(PcObject, Base, Model):
    __tablename__ = "payment_message"
    name: str = sa.Column(sa.String(50), unique=True, nullable=False)
    checksum: bytes = sa.Column(sa.LargeBinary(32), unique=True, nullable=False)


##
# When an incident is `CREATED` it can be either `CANCELLED` and it's the end of this incident. Or it can be `VALIDATED`.
##
class IncidentStatus(enum.Enum):
    CREATED = "created"
    VALIDATED = "validated"
    CANCELLED = "cancelled"


class IncidentType(enum.Enum):
    OVERPAYMENT = "overpayment"
    COMMERCIAL_GESTURE = "commercial gesture"
    OFFER_PRICE_REGULATION = "offer price regulation"
    FRAUD = "fraud"


class FinanceIncidentRequestOrigin(enum.Enum):
    FRAUDE = "Fraude"
    SUPPORT_JEUNE = "Support Jeune"
    SUPPORT_PRO = "Support Pro"


class FinanceIncident(PcObject, Base, Model):
    __tablename__ = "finance_incident"
    kind: IncidentType = sa.Column(
        sa.Enum(IncidentType, native_enum=False, create_contraint=False),
        nullable=False,
    )
    status: IncidentStatus = sa.Column(
        sa.Enum(IncidentStatus, native_enum=False, create_constraint=False),
        nullable=False,
        server_default=IncidentStatus.CREATED.value,
        default=IncidentStatus.CREATED,
    )

    venueId = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False)
    venue: sa_orm.Mapped["offerers_models.Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], backref="finance_incidents"
    )

    details: dict = sa.Column(
        sa_mutable.MutableDict.as_mutable(sa_psql.JSONB), nullable=False, default={}, server_default="{}"
    )

    forceDebitNote: bool = sa.Column(sa.Boolean, nullable=False, server_default="false", default=False)

    zendeskId: int | None = sa.Column(sa.BigInteger, nullable=True, index=True)

    origin: FinanceIncidentRequestOrigin = sa.Column(
        db_utils.MagicEnum(FinanceIncidentRequestOrigin),
        nullable=False,
        index=True,
    )

    comment: str | None = sa.Column(sa.Text, nullable=True)

    @property
    def is_partial(self) -> bool:
        return any(booking_incident.is_partial for booking_incident in self.booking_finance_incidents)

    @hybrid_property
    def relates_to_collective_bookings(self) -> bool:
        return any(booking_incident.collectiveBooking for booking_incident in self.booking_finance_incidents)

    @relates_to_collective_bookings.expression  # type: ignore[no-redef]
    def relates_to_collective_bookings(cls) -> sa.sql.elements.UnaryExpression:
        aliased_booking_finance_incident = sa_orm.aliased(BookingFinanceIncident)
        return sa.exists().where(
            aliased_booking_finance_incident.incidentId == cls.id,
            aliased_booking_finance_incident.collectiveBookingId.is_not(None),
        )

    @property
    def due_amount_by_offerer(self) -> int:
        """
        Returns the amount we want to retrieve from the offerer for this incident.
        """
        return sum(booking_incident.due_amount_by_offerer for booking_incident in self.booking_finance_incidents)

    @property
    def author_full_name(self) -> str:
        from pcapi.core.users.models import User

        author_full_name = self.details.get("author")
        if author_id := self.details.get("authorId"):
            if (
                author := db.session.query(User)
                .filter_by(id=author_id)
                .options(sa_orm.load_only(User.firstName, User.lastName))
                .one_or_none()
            ):
                author_full_name = author.full_name
        return author_full_name or ""

    @hybrid_property
    def isClosed(self) -> bool:
        # FOR REVIEW (to remove): We could have simply started from cashflow to simplify the code,
        # but this would have caused an additional request for each call
        return self.status == IncidentStatus.VALIDATED and all(
            all(
                any(
                    pricing.cashflow and pricing.cashflow.status == CashflowStatus.ACCEPTED
                    for pricing in event.pricings
                )
                for event in booking_incident.finance_events
            )
            for booking_incident in self.booking_finance_incidents
        )

    @isClosed.expression  # type: ignore[no-redef]
    def isClosed(cls) -> Exists:
        return (
            sa.exists()
            .where(BookingFinanceIncident.incidentId == cls.id)
            .where(FinanceEvent.bookingFinanceIncidentId == BookingFinanceIncident.id)
            .where(Pricing.eventId == FinanceEvent.id)
            .where(CashflowPricing.pricingId == Pricing.id)
            .where(Cashflow.id == CashflowPricing.cashflowId)
            .where(Cashflow.status == CashflowStatus.ACCEPTED)
        )

    @property
    def cashflow_batch_label(self) -> str | None:
        for booking_finance_incident in self.booking_finance_incidents:
            for finance_event in booking_finance_incident.finance_events:
                for pricing in finance_event.pricings:
                    if pricing.status in (PricingStatus.PROCESSED, PricingStatus.INVOICED):
                        for cashflow in pricing.cashflows:
                            return cashflow.batch.label
        return None

    @property
    def invoice_url(self) -> str | None:
        # flatten finance events to avoid linter's too many nested blocks warning
        finance_events: list = sum(
            [booking_finance_incident.finance_events for booking_finance_incident in self.booking_finance_incidents], []
        )
        for finance_event in finance_events:
            for pricing in finance_event.pricings:
                if pricing.status in (PricingStatus.PROCESSED, PricingStatus.INVOICED):
                    for cashflow in pricing.cashflows:
                        for invoice in cashflow.invoices:
                            return invoice.url
        return None


class BookingFinanceIncident(PcObject, Base, Model):
    __tablename__ = "booking_finance_incident"
    bookingId = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=True)
    booking: sa_orm.Mapped["bookings_models.Booking | None"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], backref="incidents"
    )

    collectiveBookingId = sa.Column(sa.BigInteger, sa.ForeignKey("collective_booking.id"), index=True, nullable=True)
    collectiveBooking: sa_orm.Mapped["educational_models.CollectiveBooking | None"] = sa_orm.relationship(
        "CollectiveBooking", foreign_keys=[collectiveBookingId], backref="incidents"
    )

    incidentId = sa.Column(sa.BigInteger, sa.ForeignKey("finance_incident.id"), index=True, nullable=False)
    incident: sa_orm.Mapped["FinanceIncident"] = sa_orm.relationship(
        "FinanceIncident", foreign_keys=[incidentId], backref="booking_finance_incidents"
    )

    beneficiaryId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True)
    beneficiary: sa_orm.Mapped["users_models.User | None"] = sa_orm.relationship(
        "User", foreign_keys=[beneficiaryId], backref="incidents"
    )

    newTotalAmount: int = sa.Column(sa.Integer, nullable=False)  # in cents

    __table_args__ = (
        # - incident is either individual or collective
        # - partial collective incident is forbidden
        sa.CheckConstraint(
            '("bookingId" IS NOT NULL AND "beneficiaryId" IS NOT NULL AND "collectiveBookingId" IS NULL) '
            'OR ("collectiveBookingId" IS NOT NULL AND "bookingId" IS NULL AND "beneficiaryId" IS NULL AND "newTotalAmount" = 0)',
            name="booking_finance_incident_check",
        ),
    )

    @property
    def due_amount_by_offerer(self) -> int:
        """
        Returns the amount we want to retrieve from the offerer.
        """
        booking = self.booking or self.collectiveBooking
        assert booking  # helps mypy, already ensured by database constraint
        return utils.to_cents(booking.total_amount) - self.newTotalAmount

    @property
    def is_partial(self) -> bool:
        """
        Returns True if the booking new amount is not 0. That means the incident is not total.
        In case the new amount is 0, it means the booking didn't occur, so the incident is total.
        """
        return self.newTotalAmount > 0
