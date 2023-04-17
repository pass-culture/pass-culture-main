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
import sqlalchemy.ext.mutable as sqla_mutable
import sqlalchemy.orm as sqla_orm

from pcapi import settings
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
import pcapi.utils.db as db_utils

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


class PricingStatus(enum.Enum):
    PENDING = "pending"
    CANCELLED = "cancelled"
    VALIDATED = "validated"
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


class BankInformation(PcObject, Base, Model):
    offererId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offerer.id"), index=True, nullable=True, unique=True)
    offerer: sqla_orm.Mapped["offerers_models.Offerer | None"] = sqla_orm.relationship(
        "Offerer", foreign_keys=[offererId], backref=sqla_orm.backref("bankInformation", uselist=False)
    )
    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True, unique=True)
    venue: sqla_orm.Mapped["offerers_models.Venue | None"] = sqla_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="bankInformation", uselist=False
    )
    iban = sqla.Column(sqla.String(27), nullable=True)
    bic = sqla.Column(sqla.String(11), nullable=True)
    applicationId = sqla.Column(sqla.Integer, nullable=True, index=True, unique=True)
    status: BankInformationStatus = sqla.Column(sqla.Enum(BankInformationStatus), nullable=False)
    dateModified = sqla.Column(sqla.DateTime, nullable=True)


class Pricing(Base, Model):
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)

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
    logs: list["PricingLog"] = sqla_orm.relationship("PricingLog", back_populates="pricing")

    __table_args__ = (
        sqla.Index("idx_uniq_booking_id", bookingId, postgresql_where=status != PricingStatus.CANCELLED, unique=True),
        sqla.CheckConstraint('num_nonnulls("bookingId", "collectiveBookingId") = 1'),
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


class PricingLine(Base, Model):
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)

    pricingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("pricing.id"), index=True, nullable=True)
    pricing: Pricing = sqla_orm.relationship("Pricing", foreign_keys=[pricingId], back_populates="lines")

    # See the note about `amount` at the beginning of this module.
    amount: int = sqla.Column(sqla.Integer, nullable=False)

    category: PricingLineCategory = sqla.Column(db_utils.MagicEnum(PricingLineCategory), nullable=False)


class PricingLog(Base, Model):
    """A pricing log is created whenever the status of a pricing
    changes.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)

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
    # A `rate` attribute (or property) must be defined by subclasses.
    # It's not defined in this abstract class because SQLAlchemy would
    # then miss the `rate` column in `CustomReimbursementRule`.

    def is_active(self, booking: "bookings_models.Booking") -> bool:
        valid_from = self.valid_from or datetime.datetime(datetime.MINYEAR, 1, 1)  # type: ignore [attr-defined]
        valid_until = self.valid_until or datetime.datetime(datetime.MAXYEAR, 1, 1)  # type: ignore [attr-defined]
        return valid_from <= booking.dateUsed < valid_until  # type: ignore [operator]

    def is_relevant(
        self,
        booking: "bookings_models.Booking",
        cumulative_revenue: decimal.Decimal,
    ) -> bool:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        raise NotImplementedError()

    def matches(self, booking: "bookings_models.Booking", cumulative_revenue: decimal.Decimal) -> bool:
        return self.is_active(booking) and self.is_relevant(booking, cumulative_revenue)

    def apply(self, booking: "bookings_models.Booking") -> decimal.Decimal:
        return decimal.Decimal(booking.total_amount * self.rate)  # type: ignore [attr-defined]

    @property
    def group(self) -> RuleGroup:
        raise NotImplementedError()


class CustomReimbursementRule(ReimbursementRule, Base, Model):
    """Some offers are linked to custom reimbursement rules that overrides
    standard reimbursement rules.

    An offer may be linked to more than one reimbursement rules, but
    only one rule can be valid at a time.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)

    offerId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offer.id"), nullable=True)

    offer: sqla_orm.Mapped["offers_models.Offer | None"] = sqla_orm.relationship(
        "Offer", foreign_keys=[offerId], backref="custom_reimbursement_rules"
    )

    offererId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offerer.id"), nullable=True)

    offerer: sqla_orm.Mapped["offerers_models.Offerer | None"] = sqla_orm.relationship(
        "Offerer", foreign_keys=[offererId], backref="custom_reimbursement_rules"
    )

    # A list of identifiers of subcategories on which the rule applies.
    # If the list is empty, the rule applies on all offers of an
    # offerer.
    subcategories: list[str] = sqla.Column(sqla_psql.ARRAY(sqla.Text()), server_default="{}")

    # FIXME (dbaty, 2022-09-21): it would be nice to move this to
    # eurocents like other models do.
    # Contrary to other models, this amount is in euros, not eurocents.
    amount: decimal.Decimal = sqla.Column(sqla.Numeric(10, 2), nullable=True)

    # rate is between 0 and 1 (included), or NULL if `amount` is set.
    rate: decimal.Decimal = sqla.Column(sqla.Numeric(5, 4), nullable=True)

    # timespan is an interval during which this rule is applicable
    # (see `is_active()` below). The lower bound is inclusive and
    # required. The upper bound is exclusive and optional. If there is
    # no upper bound, it means that the rule is still applicable.
    timespan: psycopg2.extras.DateTimeRange = sqla.Column(sqla_psql.TSRANGE)

    __table_args__ = (
        # A rule relates to an offer or an offerer, never both.
        sqla.CheckConstraint('num_nonnulls("offerId", "offererId") = 1'),
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
        cumulative_revenue: decimal.Decimal = decimal.Decimal(0),  # unused
    ) -> bool:
        if booking.stock.offerId == self.offerId:
            return True
        if self.subcategories:
            if booking.stock.offer.subcategoryId not in self.subcategories:
                return False
        if booking.offererId == self.offererId:
            return True
        return False

    def apply(self, booking: "bookings_models.Booking") -> decimal.Decimal:
        if self.amount is not None:
            return booking.quantity * self.amount
        return booking.total_amount * self.rate

    @property
    def description(self) -> str:
        raise TypeError("A custom reimbursement rule does not have any description")

    @property
    def group(self) -> RuleGroup:
        return RuleGroup.CUSTOM


class Cashflow(Base, Model):
    """A cashflow represents a specific amount money that is transferred
    between us and a third party. It may be outgoing or incoming.

    By definition a cashflow cannot be zero.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    creationDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    status: CashflowStatus = sqla.Column(db_utils.MagicEnum(CashflowStatus), index=True, nullable=False)

    # We denormalize `reimbursementPoint.bankAccountId` here because it may
    # change. Here we want to store the bank account that was used at
    # the time the cashflow was created.
    bankAccountId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("bank_information.id"), index=True, nullable=False
    )
    bankAccount: BankInformation = sqla_orm.relationship(BankInformation, foreign_keys=[bankAccountId])
    reimbursementPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=False)
    reimbursementPoint: sqla_orm.Mapped["offerers_models.Venue"] = sqla_orm.relationship(
        "Venue", foreign_keys=[reimbursementPointId]
    )

    batchId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("cashflow_batch.id"), index=True, nullable=False)
    batch: "CashflowBatch" = sqla_orm.relationship("CashflowBatch", foreign_keys=[batchId])

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

    __table_args__ = (sqla.CheckConstraint('("amount" != 0)', name="non_zero_amount_check"),)


class CashflowLog(Base, Model):
    """A cashflow log is created whenever the status of a cashflow
    changes.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
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


class CashflowBatch(Base, Model):
    """A cashflow batch groups cashflows that are sent to the bank at the
    same time (in a single file).
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    creationDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    cutoff: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, unique=True)
    label: str = sqla.Column(sqla.Text, nullable=False, unique=True)


class InvoiceLine(Base, Model):
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
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


class Invoice(Base, Model):
    """An invoice is linked to one or more cashflows and shows a summary
    of their related pricings.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    date: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    reference: str = sqla.Column(sqla.Text, nullable=False, unique=True)
    reimbursementPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=False)
    reimbursementPoint: sqla_orm.Mapped["offerers_models.Venue"] = sqla_orm.relationship(
        "Venue", foreign_keys=[reimbursementPointId]
    )
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
class Payment(Base, Model):
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
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
class PaymentStatus(Base, Model):
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    paymentId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("payment.id"), index=True, nullable=False)
    payment: Payment = sqla_orm.relationship("Payment", foreign_keys=[paymentId], backref="statuses")
    date: datetime.datetime = sqla.Column(
        sqla.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sqla.func.now()
    )
    status: TransactionStatus = sqla.Column(sqla.Enum(TransactionStatus), nullable=False)
    detail = sqla.Column(sqla.Text, nullable=True)


# `PaymentMessage` is deprecated. See comment above `Payment` model
# for further details.
class PaymentMessage(Base, Model):
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    name: str = sqla.Column(sqla.String(50), unique=True, nullable=False)
    checksum: bytes = sqla.Column(sqla.LargeBinary(32), unique=True, nullable=False)
