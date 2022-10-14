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
import sqlalchemy.orm as sqla_orm

from pcapi import settings
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
import pcapi.utils.db as db_utils


if typing.TYPE_CHECKING:
    from pcapi.core.bookings.models import Booking


class DepositType(enum.Enum):
    GRANT_15_17 = "GRANT_15_17"
    GRANT_18 = "GRANT_18"


class Deposit(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    amount: decimal.Decimal = sqla.Column(sqla.Numeric(10, 2), nullable=False)

    userId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("user.id"), index=True, nullable=False)

    user = sqla_orm.relationship("User", foreign_keys=[userId], backref="deposits")  # type: ignore [misc]

    individual_bookings = sqla_orm.relationship("IndividualBooking", back_populates="deposit")  # type: ignore [misc]

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

    recredits = sqla_orm.relationship("Recredit", order_by="Recredit.dateCreated.desc()", back_populates="deposit")  # type: ignore [misc]

    __table_args__ = (
        sqla.UniqueConstraint(
            "userId",
            "type",
            name="unique_type_per_user",
        ),
    )

    @property
    def specific_caps(self):  # type: ignore [no-untyped-def]
        from . import conf

        physical_cap = None
        digital_cap = None

        if self.type == DepositType.GRANT_18:
            if self.version == 1:
                physical_cap = conf.GRANT_18_PHYSICAL_CAP_V1
                digital_cap = conf.GRANT_18_DIGITAL_CAP_V1
            elif self.version == 2:
                physical_cap = conf.GRANT_18_PHYSICAL_CAP_V2
                digital_cap = conf.GRANT_18_DIGITAL_CAP_V2

        if self.user.departementCode == conf.WALLIS_AND_FUTUNA_DEPARTMENT_CODE:
            digital_cap = None

        return conf.BaseSpecificCaps(digital_cap=digital_cap, physical_cap=physical_cap)


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


class Recredit(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    depositId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("deposit.id"), nullable=False)

    deposit = sqla_orm.relationship("Deposit", foreign_keys=[depositId], back_populates="recredits")  # type: ignore [misc]

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


class BusinessUnitStatus(enum.Enum):
    ACTIVE = "active"
    DELETED = "deleted"


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


class BankInformation(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    offererId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offerer.id"), index=True, nullable=True, unique=True)
    offerer = sqla_orm.relationship("Offerer", foreign_keys=[offererId], backref=sqla_orm.backref("bankInformation", uselist=False))  # type: ignore [misc]
    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True, unique=True)
    venue = sqla_orm.relationship("Venue", foreign_keys=[venueId], back_populates="bankInformation", uselist=False)  # type: ignore [misc]
    iban = sqla.Column(sqla.String(27), nullable=True)
    bic = sqla.Column(sqla.String(11), nullable=True)
    applicationId = sqla.Column(sqla.Integer, nullable=True, index=True, unique=True)
    status: BankInformationStatus = sqla.Column(sqla.Enum(BankInformationStatus), nullable=False)
    dateModified = sqla.Column(sqla.DateTime, nullable=True)


class BusinessUnit(Base, Model):  # type: ignore [valid-type, misc]
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    name = sqla.Column(sqla.Text)
    siret = sqla.Column(sqla.String(14), unique=True)
    status: BusinessUnitStatus = sqla.Column(
        db_utils.MagicEnum(BusinessUnitStatus), nullable=False, server_default=BusinessUnitStatus.ACTIVE.value
    )

    bankAccountId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("bank_information.id"), index=True, nullable=True)
    bankAccount = sqla_orm.relationship(BankInformation, foreign_keys=[bankAccountId])  # type: ignore [misc]

    cashflowFrequency: Frequency = sqla.Column(
        db_utils.MagicEnum(Frequency), nullable=False, default=Frequency.EVERY_TWO_WEEKS
    )
    invoiceFrequency: Frequency = sqla.Column(
        db_utils.MagicEnum(Frequency), nullable=False, default=Frequency.EVERY_TWO_WEEKS
    )

    invoices = sqla_orm.relationship("Invoice", back_populates="businessUnit")  # type: ignore [misc]


class BusinessUnitVenueLink(Base, Model):  # type: ignore [valid-type, misc]
    """Represent the period of time during which a venue was linked to a
    specific business unit.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    venueId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=False)
    venue = sqla_orm.relationship("Venue", foreign_keys=[venueId])  # type: ignore [misc]
    businessUnitId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("business_unit.id"), index=True, nullable=False)
    businessUnit = sqla_orm.relationship("BusinessUnit", foreign_keys=[businessUnitId], backref="venue_links")  # type: ignore [misc]
    # The lower bound is inclusive and required. The upper bound is
    # exclusive and optional. If there is no upper bound, it means
    # that the venue is still linked to the business unit.
    # Because business units have been linked to venues before this
    # table was created, the lower bound was set to the Epoch for
    # existing links when this table was first populated.
    timespan: psycopg2.extras.DateTimeRange = sqla.Column(sqla_psql.TSRANGE, nullable=False)

    __table_args__ = (
        # A venue cannot be linked to multiple business units at the
        # same time.
        sqla_psql.ExcludeConstraint(("venueId", "="), ("timespan", "&&")),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)


class Pricing(Base, Model):  # type: ignore [valid-type, misc]
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)

    status: PricingStatus = sqla.Column(db_utils.MagicEnum(PricingStatus), index=True, nullable=False)

    bookingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("booking.id"), index=True, nullable=True)
    booking = sqla_orm.relationship("Booking", foreign_keys=[bookingId], backref="pricings")  # type: ignore [misc]
    collectiveBookingId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("collective_booking.id"), index=True, nullable=True
    )
    collectiveBooking = sqla_orm.relationship(  # type: ignore [misc]
        "CollectiveBooking", foreign_keys=[collectiveBookingId], backref="pricings"
    )
    # FIXME (dbaty 2022-08-03): make NOT NULLable once we have populated all rows.
    venueId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True)
    venue = sqla_orm.relationship("Venue", foreign_keys=[venueId])  # type: ignore [misc]

    # FIXME (dbaty, 2022-06-20): remove `businessUnitId` and `siret`
    # columns once we have fully switched to `pricingPointId`
    businessUnitId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("business_unit.id"), index=True, nullable=True)
    businessUnit = sqla_orm.relationship("BusinessUnit", foreign_keys=[businessUnitId])  # type: ignore [misc]
    # `siret` is either the SIRET of the venue if it has one, or the
    # SIRET of its business unit (at the time of the creation of the
    # pricing).
    siret = sqla.Column(sqla.String(14), nullable=True, index=True)
    # FIXME (dbaty, 2022-06-20): set non-NULLABLE once pricing code
    # has been updated and old data has been migrated.
    pricingPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True)
    pricingPoint = sqla_orm.relationship("Venue", foreign_keys=[pricingPointId])  # type: ignore [misc]

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
    customRule = sqla_orm.relationship("CustomReimbursementRule", foreign_keys=[customRuleId])  # type: ignore [misc]

    # Revenue is in euro cents. It's the revenue of the business unit
    # as of `pricing.valueDate` (thus including the related booking).
    # It is zero or positive.
    revenue: int = sqla.Column(sqla.Integer, nullable=False)

    cashflows = sqla_orm.relationship("Cashflow", secondary="cashflow_pricing", back_populates="pricings")  # type: ignore [misc]
    lines = sqla_orm.relationship("PricingLine", back_populates="pricing", order_by="PricingLine.id")  # type: ignore [misc]
    logs = sqla_orm.relationship("PricingLog", back_populates="pricing")  # type: ignore [misc]

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


class PricingLine(Base, Model):  # type: ignore [valid-type, misc]
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)

    pricingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("pricing.id"), index=True, nullable=True)
    pricing = sqla_orm.relationship("Pricing", foreign_keys=[pricingId], back_populates="lines")  # type: ignore [misc]

    # See the note about `amount` at the beginning of this module.
    amount: int = sqla.Column(sqla.Integer, nullable=False)

    category: PricingLineCategory = sqla.Column(db_utils.MagicEnum(PricingLineCategory), nullable=False)


class PricingLog(Base, Model):  # type: ignore [valid-type, misc]
    """A pricing log is created whenever the status of a pricing
    changes.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)

    pricingId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("pricing.id"), index=True, nullable=False)
    pricing = sqla_orm.relationship("Pricing", foreign_keys=[pricingId], back_populates="logs")  # type: ignore [misc]

    timestamp: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    statusBefore: PricingStatus = sqla.Column(db_utils.MagicEnum(PricingStatus), nullable=False)
    statusAfter: PricingStatus = sqla.Column(db_utils.MagicEnum(PricingStatus), nullable=False)
    reason: PricingLogReason = sqla.Column(db_utils.MagicEnum(PricingLogReason), nullable=False)


class ReimbursementRule:
    # A `rate` attribute (or property) must be defined by subclasses.
    # It's not defined in this abstract class because SQLAlchemy would
    # then miss the `rate` column in `CustomReimbursementRule`.

    def is_active(self, booking: "Booking") -> bool:
        valid_from = self.valid_from or datetime.datetime(datetime.MINYEAR, 1, 1)  # type: ignore [attr-defined]
        valid_until = self.valid_until or datetime.datetime(datetime.MAXYEAR, 1, 1)  # type: ignore [attr-defined]
        return valid_from <= booking.dateUsed < valid_until  # type: ignore [operator]

    def is_relevant(self, booking: "Booking", cumulative_revenue: decimal.Decimal) -> bool:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        raise NotImplementedError()

    def matches(self, booking: "Booking", cumulative_revenue="ignored") -> bool:  # type: ignore [no-untyped-def]
        return self.is_active(booking) and self.is_relevant(booking, cumulative_revenue)

    def apply(self, booking: "Booking") -> decimal.Decimal:
        return decimal.Decimal(booking.total_amount * self.rate)  # type: ignore [attr-defined]

    @property
    def group(self) -> str:
        raise NotImplementedError()


class CustomReimbursementRule(ReimbursementRule, Base, Model):  # type: ignore [valid-type, misc]
    """Some offers are linked to custom reimbursement rules that overrides
    standard reimbursement rules.

    An offer may be linked to more than one reimbursement rules, but
    only one rule can be valid at a time.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)

    offerId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offer.id"), nullable=True)

    offer = sqla_orm.relationship("Offer", foreign_keys=[offerId], backref="custom_reimbursement_rules")  # type: ignore [misc]

    offererId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("offerer.id"), nullable=True)

    offerer = sqla_orm.relationship("Offerer", foreign_keys=[offererId], backref="custom_reimbursement_rules")  # type: ignore [misc]

    # FIXME (dbaty, 2021-11-04): remove `categories` column once v161 is deployed
    categories = sqla.Column(sqla_psql.ARRAY(sqla.Text()), server_default="{}")
    # A list of identifiers of subcategories on which the rule applies.
    # If the list is empty, the rule applies on all offers of an
    # offerer.
    subcategories = sqla.Column(sqla_psql.ARRAY(sqla.Text()), server_default="{}")

    # FIXME (dbaty, 2022-09-21): it would be nice to move this to
    # eurocents like other models do.
    # Contrary to other models, this amount is in euros, not eurocents.
    amount = sqla.Column(sqla.Numeric(10, 2), nullable=True)

    # rate is between 0 and 1 (included), or NULL if `amount` is set.
    rate = sqla.Column(sqla.Numeric(5, 4), nullable=True)

    # timespan is an interval during which this rule is applicable
    # (see `is_active()` below). The lower bound is inclusive and
    # required. The upper bound is exclusive and optional. If there is
    # no upper bound, it means that the rule is still applicable.
    timespan = sqla.Column(sqla_psql.TSRANGE)

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

    def __init__(self, **kwargs):  # type: ignore [no-untyped-def]
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)

    def is_active(self, booking: "Booking"):  # type: ignore [no-untyped-def]
        if booking.dateUsed < self.timespan.lower:  # type: ignore [union-attr]
            return False
        return self.timespan.upper is None or booking.dateUsed < self.timespan.upper  # type: ignore [union-attr]

    def is_relevant(self, booking: "Booking", cumulative_revenue="ignored"):  # type: ignore [no-untyped-def]
        if booking.stock.offerId == self.offerId:
            return True
        if self.subcategories:
            if booking.stock.offer.subcategoryId not in self.subcategories:
                return False
        if booking.offererId == self.offererId:
            return True
        return False

    def apply(self, booking: "Booking"):  # type: ignore [no-untyped-def]
        if self.amount is not None:
            return booking.quantity * self.amount
        return booking.total_amount * self.rate  # type: ignore [operator]

    @property
    def description(self):  # type: ignore [no-untyped-def] # implementation of ReimbursementRule.description
        raise TypeError("A custom reimbursement rule does not have any description")

    @property
    def group(self):  # type: ignore [no-untyped-def]
        from . import conf

        return conf.RuleGroups.CUSTOM


class Cashflow(Base, Model):  # type: ignore [valid-type, misc]
    """A cashflow represents a specific amount money that is transferred
    between us and a third party. It may be outgoing or incoming.

    By definition a cashflow cannot be zero.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    creationDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    status: CashflowStatus = sqla.Column(db_utils.MagicEnum(CashflowStatus), index=True, nullable=False)

    # FIXME (dbaty, 2022-06-20): remove `businessUnitId` once we have
    # fully switched to `reimbursementPointId`
    businessUnitId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("business_unit.id"), index=True, nullable=True)
    businessUnit = sqla_orm.relationship("BusinessUnit", foreign_keys=[businessUnitId])  # type: ignore [misc]
    # We denormalize `BusinessUnit.bankAccountId` here because it may
    # change. Here we want to store the bank account that was used at
    # the time the cashflow was created.
    bankAccountId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("bank_information.id"), index=True, nullable=False
    )
    bankAccount = sqla_orm.relationship(BankInformation, foreign_keys=[bankAccountId])  # type: ignore [misc]
    # FIXME (dbaty, 2022-06-20): set non-NULLABLE once cashflow code
    # has been updated and old data has been migrated.
    reimbursementPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True)
    reimbursementPoint = sqla_orm.relationship("Venue", foreign_keys=[reimbursementPointId])  # type: ignore [misc]

    batchId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("cashflow_batch.id"), index=True, nullable=False)
    batch = sqla_orm.relationship("CashflowBatch", foreign_keys=[batchId])  # type: ignore [misc]

    # See the note about `amount` at the beginning of this module.
    # The amount cannot be zero.
    # For now, only negative (outgoing) cashflows are automatically
    # generated. Positive (incoming) cashflows are manually created.
    amount: int = sqla.Column(sqla.Integer, nullable=False)

    # The transaction id is a UUID that will be included in the wire
    # transfer file that is sent to the bank.
    transactionId: UUID = sqla.Column(
        sqla_psql.UUID(as_uuid=True), nullable=False, unique=True, server_default=sqla.func.gen_random_uuid()
    )

    logs = sqla_orm.relationship("CashflowLog", back_populates="cashflow", order_by="CashflowLog.timestamp")  # type: ignore [misc]
    pricings = sqla_orm.relationship("Pricing", secondary="cashflow_pricing", back_populates="cashflows")  # type: ignore [misc]
    invoices = sqla_orm.relationship("Invoice", secondary="invoice_cashflow", back_populates="cashflows")  # type: ignore [misc]

    __table_args__ = (sqla.CheckConstraint('("amount" != 0)', name="non_zero_amount_check"),)


class CashflowLog(Base, Model):  # type: ignore [valid-type, misc]
    """A cashflow log is created whenever the status of a cashflow
    changes.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    cashflowId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("cashflow.id"), index=True, nullable=False)
    cashflow = sqla_orm.relationship("Cashflow", foreign_keys=[cashflowId], back_populates="logs")  # type: ignore [misc]
    timestamp: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    statusBefore: CashflowStatus = sqla.Column(db_utils.MagicEnum(CashflowStatus), nullable=False)
    statusAfter: CashflowStatus = sqla.Column(db_utils.MagicEnum(CashflowStatus), nullable=False)
    details = sqla.Column(db_utils.SafeJsonB, nullable=True, default={}, server_default="{}")


class CashflowPricing(Base, Model):  # type: ignore [valid-type, misc]
    """An association table between cashflows and pricings for their
    many-to-many relationship.

    A cashflow is "naturally" linked to multiple pricings of the same
    business unit: we build a cashflow based on all pricings of a
    given period (e.g. two weeks).

    A pricing may also be linked to multiple cashflows: for example,
    if a cashflow is rejected by the bank because the bank information
    are wrong, we will create another cashflow and the pricing will
    thus be linked to two cashflows.
    """

    cashflowId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("cashflow.id"), index=True, primary_key=True)
    pricingId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("pricing.id"), index=True, primary_key=True)

    __table_args__ = (
        sqla.UniqueConstraint(
            "cashflowId",
            "pricingId",
            name="unique_cashflow_pricing_association",
        ),
    )


class CashflowBatch(Base, Model):  # type: ignore [valid-type, misc]
    """A cashflow batch groups cashflows that are sent to the bank at the
    same time (in a single file).
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    creationDate: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    cutoff: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, unique=True)
    label: str = sqla.Column(sqla.Text, nullable=False, unique=True)


class InvoiceLine(Base, Model):  # type: ignore [valid-type, misc]
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    invoiceId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("invoice.id"), index=True, nullable=False)
    invoice = sqla_orm.relationship("Invoice", foreign_keys=[invoiceId], back_populates="lines")  # type: ignore [misc]
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
    def contribution_rate(self):  # type: ignore [no-untyped-def]
        return 1 - self.rate


@dataclasses.dataclass
class InvoiceLineGroup:
    position: int
    label: str
    lines: list[InvoiceLine]
    used_bookings_subtotal: float
    contribution_subtotal: float
    reimbursed_amount_subtotal: float


class Invoice(Base, Model):  # type: ignore [valid-type, misc]
    """An invoice is linked to one or more cashflows and shows a summary
    of their related pricings.
    """

    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    date: datetime.datetime = sqla.Column(sqla.DateTime, nullable=False, server_default=sqla.func.now())
    reference: str = sqla.Column(sqla.Text, nullable=False, unique=True)
    # FIXME (dbaty, 2022-06-20): remove `businessUnitId` once we have
    # fully switched to `reimbursementPointId`
    businessUnitId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("business_unit.id"), index=True, nullable=True)
    businessUnit: "sqla_orm.Mapped[BusinessUnit]" = sqla_orm.relationship(
        "BusinessUnit", back_populates="invoices", uselist=False
    )
    # FIXME (dbaty, 2022-06-20): set non-NULLABLE once invoice code
    # has been updated and old data has been migrated.
    reimbursementPointId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("venue.id"), index=True, nullable=True)
    reimbursementPoint = sqla_orm.relationship("Venue", foreign_keys=[reimbursementPointId])  # type: ignore [misc]
    # See the note about `amount` at the beginning of this module.
    amount: int = sqla.Column(sqla.Integer, nullable=False)
    token: str = sqla.Column(sqla.Text, unique=True, nullable=False)
    lines = sqla_orm.relationship("InvoiceLine", back_populates="invoice")  # type: ignore [misc]
    cashflows = sqla_orm.relationship("Cashflow", secondary="invoice_cashflow", back_populates="invoices")  # type: ignore [misc]

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


class InvoiceCashflow(Base, Model):  # type: ignore [valid-type, misc]
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
class Payment(Base, Model):  # type: ignore [valid-type, misc]
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    bookingId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("booking.id"), index=True, nullable=True)
    booking = sqla_orm.relationship("Booking", foreign_keys=[bookingId], backref="payments")  # type: ignore [misc]
    collectiveBookingId = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("collective_booking.id"), index=True, nullable=True
    )
    collectiveBooking = sqla_orm.relationship("CollectiveBooking", foreign_keys=[collectiveBookingId], backref="payments")  # type: ignore [misc]
    # Contrary to other models, this amount is in euros, not eurocents.
    amount: decimal.Decimal = sqla.Column(sqla.Numeric(10, 2), nullable=False)
    reimbursementRule = sqla.Column(sqla.String(200))
    reimbursementRate = sqla.Column(sqla.Numeric(10, 2))
    customReimbursementRuleId = sqla.Column(
        sqla.BigInteger,
        sqla.ForeignKey("custom_reimbursement_rule.id"),
    )
    customReimbursementRule = sqla_orm.relationship(  # type: ignore [misc]
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
    transactionEndToEndId = sqla.Column(sqla_psql.UUID(as_uuid=True), nullable=True)
    transactionLabel = sqla.Column(sqla.String(140), nullable=True)
    paymentMessageId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("payment_message.id"), nullable=True)
    paymentMessage = sqla_orm.relationship(  # type: ignore [misc]
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
class PaymentStatus(Base, Model):  # type: ignore [valid-type, misc]
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    paymentId: int = sqla.Column(sqla.BigInteger, sqla.ForeignKey("payment.id"), index=True, nullable=False)
    payment = sqla_orm.relationship("Payment", foreign_keys=[paymentId], backref="statuses")  # type: ignore [misc]
    date: datetime.datetime = sqla.Column(
        sqla.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sqla.func.now()
    )
    status: TransactionStatus = sqla.Column(sqla.Enum(TransactionStatus), nullable=False)
    detail = sqla.Column(sqla.Text, nullable=True)


# `PaymentMessage` is deprecated. See comment above `Payment` model
# for further details.
class PaymentMessage(Base, Model):  # type: ignore [valid-type, misc]
    id: int = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    name: str = sqla.Column(sqla.String(50), unique=True, nullable=False)
    checksum: bytes = sqla.Column(sqla.LargeBinary(32), unique=True, nullable=False)
