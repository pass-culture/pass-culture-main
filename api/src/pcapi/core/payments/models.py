from dataclasses import dataclass
import datetime
from decimal import Decimal
import enum
import typing

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import SmallInteger

from pcapi.core.finance import conf as finance_conf
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
import pcapi.utils.db as db_utils


if typing.TYPE_CHECKING:
    from pcapi.core.bookings.models import Booking


MIN_DATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)
MAX_DATETIME = datetime.datetime(datetime.MAXYEAR, 1, 1)


class ReimbursementRule:

    # A `rate` attribute (or property) must be defined by subclasses.
    # It's not defined in this abstract class because SQLAlchemy would
    # then miss the `rate` column in `CustomReimbursementRule`.

    def is_active(self, booking: "Booking") -> bool:
        valid_from = self.valid_from or MIN_DATETIME  # type: ignore [attr-defined]
        valid_until = self.valid_until or MAX_DATETIME  # type: ignore [attr-defined]
        return valid_from <= booking.dateUsed < valid_until  # type: ignore [operator]

    def is_relevant(self, booking: "Booking", cumulative_revenue: Decimal) -> bool:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        raise NotImplementedError()

    def matches(self, booking: "Booking", cumulative_revenue="ignored") -> bool:  # type: ignore [no-untyped-def]
        return self.is_active(booking) and self.is_relevant(booking, cumulative_revenue)

    def apply(self, booking: "Booking") -> Decimal:
        return Decimal(booking.total_amount * self.rate)  # type: ignore [attr-defined]

    @property
    def group(self) -> str:
        raise NotImplementedError()


class CustomReimbursementRule(ReimbursementRule, Base, Model):  # type: ignore [valid-type, misc]
    """Some offers are linked to custom reimbursement rules that overrides
    standard reimbursement rules.

    An offer may be linked to more than one reimbursement rules, but
    only one rule can be valid at a time.
    """

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    offerId = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), nullable=True)

    offer = relationship("Offer", foreign_keys=[offerId], backref="custom_reimbursement_rules")  # type: ignore [misc]

    offererId = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), nullable=True)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref="custom_reimbursement_rules")  # type: ignore [misc]

    # FIXME (dbaty, 2021-11-04): remove `categories` column once v161 is deployed
    categories = sa.Column(postgresql.ARRAY(sa.Text()), server_default="{}")
    # A list of identifiers of subcategories on which the rule applies.
    # If the list is empty, the rule applies on all offers of an
    # offerer.
    subcategories = sa.Column(postgresql.ARRAY(sa.Text()), server_default="{}")

    amount = sa.Column(sa.Numeric(10, 2), nullable=True)

    # rate is between 0 and 1 (included), or NULL if `amount` is set.
    rate = sa.Column(sa.Numeric(5, 4), nullable=True)

    # timespan is an interval during which this rule is applicable
    # (see `is_active()` below). The lower bound is inclusive and
    # required. The upper bound is exclusive and optional. If there is
    # no upper bound, it means that the rule is still applicable.
    timespan = sa.Column(postgresql.TSRANGE)

    __table_args__ = (
        # A rule relates to an offer or an offerer, never both.
        sa.CheckConstraint('num_nonnulls("offerId", "offererId") = 1'),
        # A rule has an amount or a rate, never both.
        sa.CheckConstraint("num_nonnulls(amount, rate) = 1"),
        # A timespan must have a lower bound. Upper bound is optional.
        # Overlapping rules are rejected by `validation._check_reimbursement_rule_conflicts()`.
        sa.CheckConstraint("lower(timespan) IS NOT NULL"),
        sa.CheckConstraint("rate IS NULL OR (rate BETWEEN 0 AND 1)"),
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
        return finance_conf.RuleGroups.CUSTOM


class DepositType(enum.Enum):
    GRANT_15_17 = "GRANT_15_17"
    GRANT_18 = "GRANT_18"


class Deposit(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    amount: Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    user = relationship("User", foreign_keys=[userId], backref="deposits")  # type: ignore [misc]

    individual_bookings = relationship("IndividualBooking", back_populates="deposit")  # type: ignore [misc]

    source: str = sa.Column(sa.String(300), nullable=False)

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    dateUpdated = sa.Column(sa.DateTime, nullable=True, onupdate=sa.func.now())

    expirationDate = sa.Column(sa.DateTime, nullable=True)

    version: int = sa.Column(SmallInteger, nullable=False)

    type: DepositType = sa.Column(
        sa.Enum(DepositType, native_enum=False, create_constraint=False),
        nullable=False,
        server_default=DepositType.GRANT_18.value,
    )

    recredits = relationship("Recredit", order_by="Recredit.dateCreated.desc()", back_populates="deposit")  # type: ignore [misc]

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "type",
            name="unique_type_per_user",
        ),
    )

    @property
    def specific_caps(self):  # type: ignore [no-untyped-def]
        from . import conf

        return conf.SPECIFIC_CAPS[self.type][self.version]


@dataclass
class GrantedDeposit:
    amount: Decimal
    expiration_date: datetime.datetime
    type: DepositType
    version: int = 1


class RecreditType(enum.Enum):
    RECREDIT_16 = "Recredit16"
    RECREDIT_17 = "Recredit17"


class Recredit(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    depositId: int = sa.Column(sa.BigInteger, sa.ForeignKey("deposit.id"), nullable=False)

    deposit = relationship("Deposit", foreign_keys=[depositId], back_populates="recredits")  # type: ignore [misc]

    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    amount: Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)

    recreditType: RecreditType = sa.Column(
        sa.Enum(RecreditType, native_enum=False, create_constraint=False),
        nullable=False,
    )
