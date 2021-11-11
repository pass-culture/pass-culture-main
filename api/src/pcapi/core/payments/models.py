from dataclasses import dataclass
import datetime
from decimal import Decimal
import enum

import psycopg2.extras
import pytz
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import SmallInteger

from pcapi.core.bookings.models import Booking
from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


MIN_DATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)
MAX_DATETIME = datetime.datetime(datetime.MAXYEAR, 1, 1)


class ReimbursementRule:

    # A `rate` attribute (or property) must be defined by subclasses.
    # It's not defined in this abstract class because SQLAlchemy would
    # then miss the `rate` column in `CustomReimbursementRule`.

    def is_active(self, booking: Booking) -> bool:
        valid_from = self.valid_from or MIN_DATETIME
        valid_until = self.valid_until or MAX_DATETIME
        return valid_from <= booking.dateUsed < valid_until

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        raise NotImplementedError()

    def matches(self, booking: Booking, cumulative_revenue="ignored") -> bool:
        return self.is_active(booking) and self.is_relevant(booking, cumulative_revenue)

    def apply(self, booking: Booking) -> Decimal:
        return Decimal(booking.total_amount * self.rate)


class CustomReimbursementRule(ReimbursementRule, Model):
    """Some offers are linked to custom reimbursement rules that overrides
    standard reimbursement rules.

    An offer may be linked to more than one reimbursement rules, but
    only one rule can be valid at a time.
    """

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    offerId = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), nullable=True)

    offer = relationship("Offer", foreign_keys=[offerId], backref="custom_reimbursement_rules")

    offererId = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), nullable=True)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref="custom_reimbursement_rules")

    # FIXME (dbaty, 2021-11-04): remove `categories` column once v161 is deployed
    categories = sa.Column(postgresql.ARRAY(sa.Text()), server_default="{}")
    # A list of identifiers of subcategories on which the rule applies.
    # If the list is empty, the rule applies on all offers of an
    # offerer.
    subcategories = sa.Column(postgresql.ARRAY(sa.Text()), server_default="{}")

    amount = sa.Column(sa.Numeric(10, 2), nullable=True)

    # rate is between 0 and 1 (included), or NULL if `amount` is set.
    rate = sa.Column(sa.Numeric(3, 2), nullable=True)

    timespan = sa.Column(postgresql.TSRANGE)

    __table_args__ = (
        # A rule relates to an offer or an offerer, never both.
        sa.CheckConstraint('num_nonnulls("offerId", "offererId") = 1'),
        # A rule has an amount or a rate, never both.
        sa.CheckConstraint("num_nonnulls(amount, rate) = 1"),
        # A timespan must have a lower bound. Upper bound is optional.
        sa.CheckConstraint("lower(timespan) IS NOT NULL"),
        sa.CheckConstraint("rate IS NULL OR (rate BETWEEN 0 AND 1)"),
    )

    def __init__(self, **kwargs):
        kwargs["timespan"] = self._make_timespan(*kwargs["timespan"])
        super().__init__(**kwargs)

    @classmethod
    def _make_timespan(cls, start, end=None):
        start = start.astimezone(pytz.utc).isoformat()
        end = end.astimezone(pytz.utc).isoformat() if end else None
        return psycopg2.extras.DateTimeRange(start, end, bounds="[)")

    def is_active(self, booking: Booking):
        if booking.dateUsed < self.timespan.lower:
            return False
        return self.timespan.upper is None or booking.dateUsed < self.timespan.upper

    def is_relevant(self, booking: Booking, cumulative_revenue="ignored"):
        if booking.stock.offerId == self.offerId:
            return True
        if self.subcategories:
            if booking.stock.offer.subcategoryId not in self.subcategories:
                return False
        if booking.offererId == self.offererId:
            return True
        return False

    def apply(self, booking: Booking):
        if self.amount is not None:
            return booking.quantity * self.amount
        return booking.total_amount * self.rate

    @property
    def description(self):  # implementation of ReimbursementRule.description
        raise TypeError("A custom reimbursement rule does not have any description")


class DepositType(enum.Enum):
    GRANT_15_17 = "GRANT_15_17"
    GRANT_18 = "GRANT_18"


class Deposit(PcObject, Model):
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    amount = sa.Column(sa.Numeric(10, 2), nullable=False)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    user = relationship("User", foreign_keys=[userId], backref="deposits")

    individual_bookings = relationship("IndividualBooking", back_populates="deposit")

    source = sa.Column(sa.String(300), nullable=False)

    dateCreated = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    dateUpdated = sa.Column(sa.DateTime, nullable=True, onupdate=sa.func.now())

    expirationDate = sa.Column(sa.DateTime, nullable=True)

    version = sa.Column(SmallInteger, nullable=False)

    type = sa.Column(
        "type",
        sa.Enum(DepositType, native_enum=False, create_constraint=False),
        nullable=False,
        server_default=DepositType.GRANT_18.value,
    )

    recredits = relationship("Recredit", order_by="Recredit.dateCreated.desc()")

    @property
    def specific_caps(self):
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


class Recredit(PcObject, Model):
    depositId = sa.Column(sa.BigInteger, sa.ForeignKey("deposit.id"), nullable=False)

    deposit = relationship("Deposit", foreign_keys=[depositId])

    dateCreated = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    amount = sa.Column(sa.Numeric(10, 2), nullable=False)

    recreditType = sa.Column(
        "recreditType",
        sa.Enum(RecreditType, native_enum=False, create_constraint=False),
        nullable=False,
    )
