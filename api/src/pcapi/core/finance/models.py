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
import sqlalchemy as sqla
import sqlalchemy.dialects.postgresql as sqla_psql
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.ext.mutable as sqla_mutable
import sqlalchemy.orm as sqla_orm
from sqlalchemy.sql.selectable import Exists

from pcapi import settings
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject
import pcapi.utils.db as db_utils

from . import utils
from .enum import DepositType


if typing.TYPE_CHECKING:
    import pcapi.core.bookings.models as bookings_models
    import pcapi.core.educational.models as educational_models
    import pcapi.core.offerers.models as offerers_models
    import pcapi.core.offers.models as offers_models
    import pcapi.core.users.models as users_models

    from . import conf


class Deposit(PcObject, Base, Model):
    amount: decimal.Decimal = sqla.Column(sqla.Numeric(10, 2), nullable=False)

    userId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("user.id"), index=True, nullable=False)

    user: "users_models.User" = sqla_orm.relationship("User", foreign_keys=[userId], backref="deposits")

    bookings: list["bookings_models.Booking"] = sqla_orm.relationship("Booking", back_populates="deposit")

    source: str = sqla.Column(sqla.String(300), nullable=False)

    dateCreated: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())

    dateUpdated = sqla.Column(sqla.DateTime, nullable=True, onupdate=sqla.func.now())

    expirationDate = sqla.Column(sqla.DateTime, nullable=True)

    version: int = sqla.Column(sqla.SmallInteger, nullable=False)

    type: DepositType = sqla.Column(
        sqla.Enum(DepositType, native_enum=False, create_constraint=False),
        nullable=False,
        server_default=DepositType.GRANT_18.value,
    )

    recredits: list["Recredit"] = sqla_orm.relationship(
        "Recredit", order_by="Recredit.dateCreated.desc()", back_populates="deposit"
    )

    __table_args__ = (
        sqla.UniqueConstraint(
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

        if self.version == 1:
            physical_cap = conf.GRANT_18_PHYSICAL_CAP_V1
            digital_cap = conf.GRANT_18_DIGITAL_CAP_V1
        elif self.version == 2:
            physical_cap = conf.GRANT_18_PHYSICAL_CAP_V2
            digital_cap = conf.GRANT_18_DIGITAL_CAP_V2

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
    MANUAL_MODIFICATION = "ManualModification"


class Recredit(PcObject, Base, Model):
    depositId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("deposit.id"), nullable=False)

    deposit: Deposit = sqla_orm.relationship("Deposit", foreign_keys=[depositId], back_populates="recredits")

    dateCreated: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())

    amount: decimal.Decimal = sqla.Column(sqla.Numeric(10, 2), nullable=False)

    recreditType: RecreditType = sqla.Column(
        sqla.Enum(RecreditType, native_enum=False, create_constraint=False),
        nullable=False,
    )

    comment = sqla.Column(sqla.Text, nullable=True)


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
    PENDING = "pending"  # blocked, will not be taken in account in next cashflow
    CANCELLED = "cancelled"
    VALIDATED = "validated"  # will be taken in account in next cashflow
    REJECTED = "rejected"
    PROCESSED = "processed"  # has an associated cashflow
    INVOICED = "invoiced"  # has an associated invoice (whose cashflows are "accepted")


CANCELLABLE_PRICING_STATUSES = {PricingStatus.PENDING, PricingStatus.VALIDATED, PricingStatus.REJECTED}
DELETABLE_PRICING_STATUSES = CANCELLABLE_PRICING_STATUSES | {PricingStatus.CANCELLED}


class PricingLineCategory(enum.Enum):
    OFFERER_REVENUE = "offerer revenue"
    OFFERER_CONTRIBUTION = "offerer contribution"
    PASS_CULTURE_COMMISSION = "pass culture commission"


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
    # And it's finally sent to the bank. By default, we decide it's
    # accepted. The bank will inform us later if it rejected the
    # cashflow. (For now, this happens outside of this application,
    # which is why there is no "rejected" status below for now.)
    ACCEPTED = "accepted"


class BankInformationStatus(enum.Enum):
    REJECTED = "REJECTED"
    DRAFT = "DRAFT"
    ACCEPTED = "ACCEPTED"


class BankAccountApplicationStatus(enum.Enum):
    DRAFT = "en_construction"
    ON_GOING = "en_instruction"
    ACCEPTED = "accepte"
    REFUSED = "refuse"
    WITHOUT_CONTINUATION = "sans_suite"
    WITH_PENDING_CORRECTIONS = "a_corriger"


class BankInformation(PcObject, Base, Model):
    offererId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offerer.id"), index=True, nullable=True)
    offerer: sqla_orm.Mapped["offerers_models.Offerer | None"] = sqla_orm.relationship(
        "Offerer", foreign_keys=[offererId], backref=sqla_orm.backref("bankInformation", uselist=False)
    )
    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True, unique=True)
    venue: sqla_orm.Mapped["offerers_models.Venue | None"] = sqla_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="bankInformation", uselist=False
    )
    iban = sqla.Column(sqla.String(27), nullable=True)
    bic = sqla.Column(sqla.String(11), nullable=True)
    applicationId: int | None = sqla.Column(sqla.Integer, nullable=True, index=True, unique=True)
    status: BankInformationStatus = sqla.Column(sqla.Enum(BankInformationStatus), nullable=False)
    dateModified = sqla.Column(sqla.DateTime, nullable=True)


class BankAccount(PcObject, Base, Model, DeactivableMixin):
    label: str = sqla.Column(sqla.String(100), nullable=False)
    offererId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    offerer: sqla_orm.Mapped["offerers_models.Offerer"] = sqla_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="bankAccounts"
    )
    iban: str = sqla.Column(sqla.String(27), nullable=False)
    bic: str = sqla.Column(sqla.String(11), nullable=False)
    dsApplicationId: int | None = sqla.Column(sqla.BigInteger, nullable=True, unique=True)
    status: BankAccountApplicationStatus = sqla.Column(sqla.Enum(BankAccountApplicationStatus), nullable=False)
    dateCreated: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    dateLastStatusUpdate: datetime.datetime = sqla.Column(sqla.DateTime)
    venueLinks: sqla_orm.Mapped[list["offerers_models.VenueBankAccountLink"]] = sqla_orm.relationship(
        "VenueBankAccountLink", back_populates="bankAccount", passive_deletes=True
    )
    statusHistory: list["BankAccountStatusHistory"] = sqla_orm.relationship(
        "BankAccountStatusHistory",
        back_populates="bankAccount",
        foreign_keys="BankAccountStatusHistory.bankAccountId",
        uselist=True,
    )

    @property
    def current_link(self) -> "offerers_models.VenueBankAccountLink | None":
        for link in self.venueLinks:
            if link.timespan.upper is None and link.timespan.lower <= datetime.datetime.utcnow():
                return link
        return None


class BankAccountStatusHistory(PcObject, Base, Model):
    bankAccountId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("bank_account.id", ondelete="CASCADE"), index=True, nullable=False
    )
    bankAccount: sqla_orm.Mapped[BankAccount] = sqla_orm.relationship(
        BankAccount, foreign_keys=[bankAccountId], back_populates="statusHistory"
    )
    status: BankAccountApplicationStatus = sqla.Column(sqla.Enum(BankAccountApplicationStatus), nullable=False)
    timespan: psycopg2.extras.DateTimeRange = sqla.Column(sqla_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # One status at a time per bank account.
        sqla_psql.ExcludeConstraint(("bankAccountId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class FinanceEvent(PcObject, Base, Model):

    creationDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    # In most cases, `valueDate` is `Booking.dateUsed` but it's useful
    # to denormalize it here: many queries use this column and we thus
    # avoid a JOIN.
    valueDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False)
    # The date that is used to price events in a determined, stable order.
    pricingOrderingDate: datetime.datetime | None = sqla.Column(sqla.DateTime, nullable=True)

    status: FinanceEventStatus = sqla.Column(db_utils.MagicEnum(FinanceEventStatus), index=True, nullable=False)
    motive: FinanceEventMotive = sqla.Column(db_utils.MagicEnum(FinanceEventMotive), nullable=False)

    bookingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("booking.id"), index=True, nullable=True)
    booking: sqla_orm.Mapped["bookings_models.Booking | None"] = sqla_orm.relationship(
        "Booking", foreign_keys=[bookingId], backref="finance_events"
    )
    collectiveBookingId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("collective_booking.id"), index=True, nullable=True
    )
    collectiveBooking: sqla_orm.Mapped["educational_models.CollectiveBooking | None"] = sqla_orm.relationship(
        "CollectiveBooking", foreign_keys=[collectiveBookingId], backref="finance_events"
    )
    bookingFinanceIncidentId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("booking_finance_incident.id"), index=True, nullable=True
    )
    bookingFinanceIncident: sqla_orm.Mapped["BookingFinanceIncident | None"] = sqla_orm.relationship(
        "BookingFinanceIncident", foreign_keys=[bookingFinanceIncidentId], backref="finance_events"
    )

    # `venueId` is denormalized and comes from `booking.venueId`
    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True)
    venue: sqla_orm.Mapped["offerers_models.Venue | None"] = sqla_orm.relationship("Venue", foreign_keys=[venueId])
    # `pricingPointId` may be None if the related venue did not have
    # any pricing point when the finance event occurred. If so, it
    # will be populated later from `link_venue_to_pricing_point()`.
    pricingPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True)
    pricingPoint: sqla_orm.Mapped["offerers_models.Venue | None"] = sqla_orm.relationship(
        "Venue", foreign_keys=[pricingPointId]
    )

    __table_args__ = (
        # An event relates to an individual or a collective booking, never both.
        sqla.CheckConstraint('num_nonnulls("bookingId", "collectiveBookingId", "bookingFinanceIncidentId") = 1'),
        # There cannot be two pending or ready events for the same individual booking.
        sqla.Index(
            "idx_uniq_individual_booking_id",
            bookingId,
            postgresql_where=status.in_((FinanceEventStatus.PENDING, FinanceEventStatus.READY)),
            unique=True,
        ),
        # Ditto for collective bookings.
        sqla.Index(
            "idx_uniq_collective_booking_id",
            collectiveBookingId,
            postgresql_where=status.in_((FinanceEventStatus.PENDING, FinanceEventStatus.READY)),
            unique=True,
        ),
        # Ditto for booking finance incidents.
        sqla.Index(
            "idx_uniq_booking_finance_incident_id",
            bookingFinanceIncidentId,
            motive,
            postgresql_where=status.in_((FinanceEventStatus.PENDING, FinanceEventStatus.READY)),
            unique=True,
        ),
        # Check status / pricingPointId / pricingOrderingDate consistency.
        sqla.CheckConstraint(
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


class Pricing(PcObject, Base, Model):

    status: PricingStatus = sqla.Column(db_utils.MagicEnum(PricingStatus), index=True, nullable=False)

    bookingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("booking.id"), index=True, nullable=True)
    booking: sqla_orm.Mapped["bookings_models.Booking | None"] = sqla_orm.relationship(
        "Booking", foreign_keys=[bookingId], backref="pricings"
    )
    collectiveBookingId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("collective_booking.id"), index=True, nullable=True
    )
    collectiveBooking: sqla_orm.Mapped["educational_models.CollectiveBooking | None"] = sqla_orm.relationship(
        "CollectiveBooking", foreign_keys=[collectiveBookingId], backref="pricings"
    )
    eventId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("finance_event.id"), index=True, nullable=False)
    event: sqla_orm.Mapped[FinanceEvent] = sqla_orm.relationship(
        "FinanceEvent", foreign_keys=[eventId], backref="pricings"
    )

    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=False)
    venue: sqla_orm.Mapped["offerers_models.Venue"] = sqla_orm.relationship("Venue", foreign_keys=[venueId])

    pricingPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=False)
    pricingPoint: sqla_orm.Mapped["offerers_models.Venue"] = sqla_orm.relationship(
        "Venue", foreign_keys=[pricingPointId]
    )

    creationDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    # `valueDate` is `Booking.dateUsed` but it's useful to denormalize
    # it here: many queries use this column and we thus avoid a JOIN.
    valueDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False)

    # See the note about `amount` at the beginning of this module.
    # The amount is zero for bookings that are not reimbursable. We do
    # create 0-pricings for these bookings to avoid processing them
    # again and again.
    amount: int = sqla.Column(sqla.Integer, nullable=False)
    # See constraints below about the relationship between rate,
    # standardRule and customRuleId.
    standardRule: str = sqla.Column(sqla.Text, nullable=False)
    customRuleId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("custom_reimbursement_rule.id"), index=True, nullable=True
    )
    customRule: sqla_orm.Mapped["CustomReimbursementRule | None"] = sqla_orm.relationship(
        "CustomReimbursementRule", foreign_keys=[customRuleId]
    )

    # Revenue is in euro cents. It's the revenue of the pricing point
    # as of `pricing.valueDate` (thus including the related booking).
    # It is zero or positive.
    revenue: int = sqla.Column(sqla.Integer, nullable=False)

    cashflows: list["Cashflow"] = sqla_orm.relationship(
        "Cashflow", secondary="cashflow_pricing", back_populates="pricings"
    )
    lines: list["PricingLine"] = sqla_orm.relationship(
        "PricingLine", back_populates="pricing", order_by="PricingLine.id"
    )
    logs: list["PricingLog"] = sqla_orm.relationship(
        "PricingLog", back_populates="pricing", order_by="PricingLog.timestamp"
    )

    __table_args__ = (
        sqla.Index("idx_uniq_booking_id", bookingId, postgresql_where=status != PricingStatus.CANCELLED, unique=True),
        sqla.CheckConstraint(
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


class PricingLine(PcObject, Base, Model):

    pricingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("pricing.id"), index=True, nullable=True)
    pricing: Pricing = sqla_orm.relationship("Pricing", foreign_keys=[pricingId], back_populates="lines")

    # See the note about `amount` at the beginning of this module.
    amount: int = sqla.Column(sqla.Integer, nullable=False)

    category: PricingLineCategory = sqla.Column(db_utils.MagicEnum(PricingLineCategory), nullable=False)


class PricingLog(PcObject, Base, Model):
    """A pricing log is created whenever the status of a pricing
    changes.
    """

    pricingId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("pricing.id"), index=True, nullable=False)
    pricing: Pricing = sqla_orm.relationship("Pricing", foreign_keys=[pricingId], back_populates="logs")

    timestamp: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    statusBefore: PricingStatus = sqla.Column(db_utils.MagicEnum(PricingStatus), nullable=False)
    statusAfter: PricingStatus = sqla.Column(db_utils.MagicEnum(PricingStatus), nullable=False)
    reason: PricingLogReason = sqla.Column(db_utils.MagicEnum(PricingLogReason), nullable=False)


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
        base = custom_total_amount or utils.to_eurocents(booking.total_amount)
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

    offerId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offer.id"), nullable=True)

    offer: sqla_orm.Mapped["offers_models.Offer | None"] = sqla_orm.relationship(
        "Offer", foreign_keys=[offerId], backref="custom_reimbursement_rules"
    )

    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), nullable=True)

    venue: sqla_orm.Mapped["offerers_models.Venue | None"] = sqla_orm.relationship(
        "Venue", foreign_keys=[venueId], backref="custom_reimbursement_rules"
    )

    offererId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offerer.id"), nullable=True)

    offerer: sqla_orm.Mapped["offerers_models.Offerer | None"] = sqla_orm.relationship(
        "Offerer", foreign_keys=[offererId], backref="custom_reimbursement_rules"
    )

    # A list of identifiers of subcategories on which the rule applies.
    # If the list is empty, the rule applies on all offers of an
    # offerer.
    subcategories: list[str] = sqla.Column(sqla_psql.ARRAY(sqla.Text()), server_default="{}")

    # The amount of the reimbursement, or NULL if `rate` is set.
    amount: int = sqla.Column(sqla.Integer, nullable=True)
    # rate is between 0 and 1 (included), or NULL if `amount` is set.
    rate: decimal.Decimal = sqla.Column(sqla.Numeric(5, 4), nullable=True)

    # timespan is an interval during which this rule is applicable
    # (see `is_active()` below). The lower bound is inclusive and
    # required. The upper bound is exclusive and optional. If there is
    # no upper bound, it means that the rule is still applicable.
    timespan: psycopg2.extras.DateTimeRange = sqla.Column(sqla_psql.TSRANGE)

    __table_args__ = (
        # A rule relates to an offer, a venue, or an offerer, never more than one.
        sqla.CheckConstraint('num_nonnulls("offerId", "venueId", "offererId") = 1'),
        # A rule has an amount or a rate, never both.
        sqla.CheckConstraint("num_nonnulls(amount, rate) = 1"),
        # A timespan must have a lower bound. Upper bound is optional.
        # Overlapping rules are rejected by `validation._check_reimbursement_rule_conflicts()`.
        sqla.CheckConstraint("lower(timespan) IS NOT NULL"),
        sqla.CheckConstraint("rate IS NULL OR (rate BETWEEN 0 AND 1)"),
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

sqla.event.listen(CustomReimbursementRule.__table__, "after_create", sqla.DDL(CustomReimbursementRule.trig_ddl))


class Cashflow(PcObject, Base, Model):
    """A cashflow represents a specific amount money that is transferred
    between us and a third party. It may be outgoing or incoming.

    Cashflows with zero amount are there to enable generating invoices lines with 100% offerer contribution
    """

    creationDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    status: CashflowStatus = sqla.Column(db_utils.MagicEnum(CashflowStatus), index=True, nullable=False)

    # We denormalize `reimbursementPoint.bankInformationId` here because it may
    # change. Here we want to store the bank account that was used at
    # the time the cashflow was created.
    bankInformationId: int = sqla.Column(
        "bankInformationId", sqla.BigInteger, sqla.ForeignKey("bank_information.id"), index=True, nullable=True
    )
    bankInformation: BankInformation = sqla_orm.relationship(BankInformation, foreign_keys=[bankInformationId])
    bankAccountId: int = sqla.Column(
        "bankAccountId", sqla.BigInteger, sqla.ForeignKey("bank_account.id"), index=True, nullable=True
    )
    bankAccount: BankAccount = sqla_orm.relationship(BankAccount, foreign_keys=[bankAccountId])
    reimbursementPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True)
    reimbursementPoint: sqla_orm.Mapped["offerers_models.Venue"] = sqla_orm.relationship(
        "Venue", foreign_keys=[reimbursementPointId]
    )

    batchId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("cashflow_batch.id"), index=True, nullable=False)
    batch: "CashflowBatch" = sqla_orm.relationship("CashflowBatch", foreign_keys=[batchId], backref="cashflows")

    # See the note about `amount` at the beginning of this module.
    # The amount cannot be zero.
    # For now, only negative (outgoing) cashflows are automatically
    # generated. Positive (incoming) cashflows are manually created.
    amount: int = sqla.Column(sqla.Integer, nullable=False)

    logs: list["CashflowLog"] = sqla_orm.relationship(
        "CashflowLog", back_populates="cashflow", order_by="CashflowLog.timestamp"
    )
    pricings: list[Pricing] = sqla_orm.relationship("Pricing", secondary="cashflow_pricing", back_populates="cashflows")
    invoices: list["Invoice"] = sqla_orm.relationship(
        "Invoice", secondary="invoice_cashflow", back_populates="cashflows"
    )


class CashflowLog(PcObject, Base, Model):
    """A cashflow log is created whenever the status of a cashflow
    changes.
    """

    cashflowId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("cashflow.id"), index=True, nullable=False)
    cashflow: list[Cashflow] = sqla_orm.relationship("Cashflow", foreign_keys=[cashflowId], back_populates="logs")
    timestamp: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    statusBefore: CashflowStatus = sqla.Column(db_utils.MagicEnum(CashflowStatus), nullable=False)
    statusAfter: CashflowStatus = sqla.Column(db_utils.MagicEnum(CashflowStatus), nullable=False)
    details: dict | None = sqla.Column(
        sqla_mutable.MutableDict.as_mutable(sqla_psql.JSONB), nullable=True, default={}, server_default="{}"
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

    cashflowId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("cashflow.id"), index=True, primary_key=True)
    pricingId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("pricing.id"), index=True, primary_key=True)


class CashflowBatch(PcObject, Base, Model):
    """A cashflow batch groups cashflows that are sent to the bank at the
    same time (in a single file).
    """

    creationDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    cutoff: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, unique=True)
    label: str = sqla.Column(sqla.Text, nullable=False, unique=True)


class InvoiceLine(PcObject, Base, Model):
    invoiceId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("invoice.id"), index=True, nullable=False)
    invoice: "Invoice" = sqla_orm.relationship("Invoice", foreign_keys=[invoiceId], back_populates="lines")
    label: str = sqla.Column(sqla.Text, nullable=False)
    # a group is a dict of label and position, as defined in ..conf.InvoiceLineGroup
    group: dict = sqla.Column(sqla_psql.JSONB, nullable=False)
    contributionAmount: int = sqla.Column(sqla.Integer, nullable=False)
    reimbursedAmount: int = sqla.Column(sqla.Integer, nullable=False)
    rate: decimal.Decimal = sqla.Column(
        sqla.Numeric(5, 4, asdecimal=True),
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

    date: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    reference: str = sqla.Column(sqla.Text, nullable=False, unique=True)
    reimbursementPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True)
    reimbursementPoint: sqla_orm.Mapped["offerers_models.Venue"] = sqla_orm.relationship(
        "Venue", foreign_keys=[reimbursementPointId]
    )
    bankAccountId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("bank_account.id"), index=True, nullable=True)
    bankAccount: BankAccount = sqla_orm.relationship("BankAccount", foreign_keys=[bankAccountId])
    # See the note about `amount` at the beginning of this module.
    amount: int = sqla.Column(sqla.Integer, nullable=False)
    token: str = sqla.Column(sqla.Text, unique=True, nullable=False)
    lines: list[InvoiceLine] = sqla_orm.relationship("InvoiceLine", back_populates="invoice")
    cashflows: list[Cashflow] = sqla_orm.relationship(
        "Cashflow", secondary="invoice_cashflow", back_populates="invoices"
    )

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


class InvoiceCashflow(Base, Model):
    """An association table between invoices and cashflows for their many-to-many relationship."""

    invoiceId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("invoice.id"), index=True, primary_key=True)
    cashflowId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("cashflow.id"), index=True, primary_key=True)

    __table_args__ = (
        sqla.PrimaryKeyConstraint(
            "invoiceId",
            "cashflowId",
            name="unique_invoice_cashflow_association",
        ),
    )


# "Payment", "PaymentStatus" and "PaymentMessage" are deprecated. They
# were used in the "old" reimbursement system. No new data is created
# with these models since 2022-01-01. These models have been replaced
# by `Pricing`, `Cashflow` and other models listed above.
class Payment(PcObject, Base, Model):
    bookingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("booking.id"), index=True, nullable=True)
    booking: "bookings_models.Booking" = sqla_orm.relationship("Booking", foreign_keys=[bookingId], backref="payments")
    collectiveBookingId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("collective_booking.id"), index=True, nullable=True
    )
    collectiveBooking: "educational_models.CollectiveBooking" = sqla_orm.relationship(
        "CollectiveBooking",
        foreign_keys=[collectiveBookingId],
        backref="payments",
    )
    # Contrary to other models, this amount is in euros, not eurocents.
    amount: decimal.Decimal = sqla.Column(sqla.Numeric(10, 2), nullable=False)
    reimbursementRule = sqla.Column(sqla.String(200))
    reimbursementRate = sqla.Column(sqla.Numeric(10, 2))
    customReimbursementRuleId = sqla.Column(
        sqla.BigInteger,
        sqla.ForeignKey("custom_reimbursement_rule.id"),
    )
    customReimbursementRule: CustomReimbursementRule | None = sqla_orm.relationship(
        "CustomReimbursementRule", foreign_keys=[customReimbursementRuleId], backref="payments"
    )
    recipientName: str = sqla.Column(sqla.String(140), nullable=False)
    recipientSiren: str = sqla.Column(sqla.String(9), nullable=False)
    iban = sqla.Column(sqla.String(27), nullable=True)
    bic = sqla.Column(
        sqla.String(11),
        sqla.CheckConstraint(
            "(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)",
            name="check_iban_and_bic_xor_not_iban_and_not_bic",
        ),
        nullable=True,
    )
    comment = sqla.Column(sqla.Text, nullable=True)
    author: str = sqla.Column(sqla.String(27), nullable=False)
    transactionEndToEndId: UUID = sqla.Column(sqla_psql.UUID(as_uuid=True), nullable=True)
    transactionLabel = sqla.Column(sqla.String(140), nullable=True)
    paymentMessageId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("payment_message.id"), nullable=True)
    paymentMessage: "PaymentMessage" = sqla_orm.relationship(
        "PaymentMessage", foreign_keys=[paymentMessageId], backref=sqla_orm.backref("payments")
    )
    batchDate = sqla.Column(sqla.DateTime, nullable=True, index=True)

    __table_args__ = (
        sqla.CheckConstraint(
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
    paymentId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("payment.id"), index=True, nullable=False)
    payment: Payment = sqla_orm.relationship("Payment", foreign_keys=[paymentId], backref="statuses")
    date: datetime.datetime = sqla.Column(
        sqla.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sqla.func.now()
    )
    status: TransactionStatus = sqla.Column(sqla.Enum(TransactionStatus), nullable=False)
    detail = sqla.Column(sqla.VARCHAR(), nullable=True)


# `PaymentMessage` is deprecated. See comment above `Payment` model
# for further details.
class PaymentMessage(PcObject, Base, Model):
    name: str = sqla.Column(sqla.String(50), unique=True, nullable=False)
    checksum: bytes = sqla.Column(sqla.LargeBinary(32), unique=True, nullable=False)


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


class FinanceIncident(PcObject, Base, Model):
    kind: IncidentType = sqla.Column(
        sqla.Enum(IncidentType, native_enum=False, create_contraint=False),
        nullable=False,
    )
    status: IncidentStatus = sqla.Column(
        sqla.Enum(IncidentStatus, native_enum=False, create_constraint=False),
        nullable=False,
        server_default=IncidentStatus.CREATED.value,
        default=IncidentStatus.CREATED,
    )

    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), nullable=False)
    venue: sqla_orm.Mapped["offerers_models.Venue | None"] = sqla_orm.relationship(
        "Venue", foreign_keys=[venueId], backref="finance_incidents"
    )

    details: dict = sqla.Column(
        sqla_mutable.MutableDict.as_mutable(sqla_psql.JSONB), nullable=False, default={}, server_default="{}"
    )

    forceDebitNote: bool = sqla.Column(sqla.Boolean, nullable=False, server_default="false", default=False)

    @property
    def is_partial(self) -> bool:
        return any(booking_incident.is_partial for booking_incident in self.booking_finance_incidents)

    @property
    def relates_to_collective_bookings(self) -> bool:
        return any(booking_incident.collectiveBooking for booking_incident in self.booking_finance_incidents)

    @property
    def due_amount_by_offerer(self) -> int:
        """
        Returns the amount we want to retrieve from the offerer for this incident.
        """
        return sum(
            utils.to_eurocents((booking_incident.booking or booking_incident.collectiveBooking).total_amount)
            - booking_incident.newTotalAmount
            for booking_incident in self.booking_finance_incidents
        )

    @property
    def commercial_gesture_amount(self) -> int:
        return sum(
            booking_finance_incident.commercial_gesture_amount
            for booking_finance_incident in self.booking_finance_incidents
        )

    @property
    def author_full_name(self) -> str:
        from pcapi.core.users.models import User

        author_full_name = self.details.get("author")
        if author_id := self.details.get("authorId"):
            if (
                author := User.query.filter_by(id=author_id)
                .options(sqla_orm.load_only(User.firstName, User.lastName))
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
    def isClosed(cls) -> Exists:  # pylint: disable=no-self-argument
        return (
            sqla.exists()
            .where(BookingFinanceIncident.incidentId == cls.id)
            .where(FinanceEvent.bookingFinanceIncidentId == BookingFinanceIncident.id)
            .where(Pricing.eventId == FinanceEvent.id)
            .where(CashflowPricing.pricingId == Pricing.id)
            .where(Cashflow.id == CashflowPricing.cashflowId)
            .where(Cashflow.status == CashflowStatus.ACCEPTED)
        )


class BookingFinanceIncident(PcObject, Base, Model):

    bookingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("booking.id"), index=True, nullable=True)
    booking: sqla_orm.Mapped["bookings_models.Booking | None"] = sqla_orm.relationship(
        "Booking", foreign_keys=[bookingId], backref="incidents"
    )

    collectiveBookingId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("collective_booking.id"), index=True, nullable=True
    )
    collectiveBooking: sqla_orm.Mapped["educational_models.CollectiveBooking | None"] = sqla_orm.relationship(
        "CollectiveBooking", foreign_keys=[collectiveBookingId], backref="incidents"
    )

    incidentId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("finance_incident.id"), index=True, nullable=False)
    incident: sqla_orm.Mapped["FinanceIncident"] = sqla_orm.relationship(
        "FinanceIncident", foreign_keys=[incidentId], backref="booking_finance_incidents"
    )

    beneficiaryId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("user.id"), index=True, nullable=True)
    beneficiary: sqla_orm.Mapped["users_models.User | None"] = sqla_orm.relationship(
        "User", foreign_keys=[beneficiaryId], backref="incidents"
    )

    newTotalAmount: int = sqla.Column(sqla.Integer, nullable=False)  # in cents

    __table_args__ = (
        # - incident is either individual or collective
        # - partial collective incident is forbidden
        sqla.CheckConstraint(
            '("bookingId" IS NOT NULL AND "beneficiaryId" IS NOT NULL AND "collectiveBookingId" IS NULL) '
            'OR ("collectiveBookingId" IS NOT NULL AND "bookingId" IS NULL AND "beneficiaryId" IS NULL AND "newTotalAmount" = 0)',
            name="booking_finance_incident_check",
        ),
    )

    @property
    def commercial_gesture_amount(self) -> int | None:  # in cents
        # Evaluates to None if the incident is not a commercial gesture
        # A commercial gesture's amount is the value we want to give to the offerer.
        # We store in  `newTotalAmount` what should have been the booking amount.
        # `commercial_gesture_amount` is thus always a negative amount.
        if self.incident.kind == IncidentType.COMMERCIAL_GESTURE:
            return utils.to_eurocents((self.booking or self.collectiveBooking).total_amount) - self.newTotalAmount
        return None

    @property
    def is_partial(self) -> bool:
        """
        Returns True if the booking new amount is not 0. That means the incident is not total.
        In case the new amount is 0, it means the booking didn't occur, so the incident is total.
        """
        return self.newTotalAmount > 0
