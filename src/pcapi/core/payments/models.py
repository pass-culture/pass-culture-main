import datetime
from decimal import Decimal
import enum

import psycopg2.extras
from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import SmallInteger

from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
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

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    offerId = Column(BigInteger, ForeignKey("offer.id"), nullable=True)

    offer = relationship("Offer", foreign_keys=[offerId], backref="custom_reimbursement_rules")

    offererId = Column(BigInteger, ForeignKey("offerer.id"), nullable=True)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref="custom_reimbursement_rules")

    # A list of identifiers of categories for which the rule applies.
    # If the list is empty, the rule applies on all offers of an
    # offerer.
    categories = Column(postgresql.ARRAY(Text()), server_default="{}")

    amount = Column(Numeric(10, 2), nullable=True)

    # rate is between 0 and 1 (included), or NULL if `amount` is set.
    rate = Column(Numeric(3, 2), nullable=True)

    timespan = Column(postgresql.TSRANGE)

    __table_args__ = (
        # A rule relates to an offer or an offerer, never both.
        CheckConstraint('num_nonnulls("offerId", "offererId") = 1'),
        # A rule has an amount or a rate, never both.
        CheckConstraint("num_nonnulls(amount, rate) = 1"),
        # A timespan must have a lower bound. Upper bound is optional.
        CheckConstraint("lower(timespan) IS NOT NULL"),
        CheckConstraint("rate IS NULL OR (rate BETWEEN 0 AND 1)"),
    )

    def __init__(self, **kwargs):
        kwargs["timespan"] = self._make_timespan(*kwargs["timespan"])
        super().__init__(**kwargs)

    @classmethod
    def _make_timespan(cls, start, end=None):
        return psycopg2.extras.DateTimeRange(start.isoformat(), end.isoformat() if end else None, bounds="[)")

    def is_active(self, booking: Booking):
        if booking.dateUsed < self.timespan.lower:
            return False
        return self.timespan.upper is None or booking.dateUsed < self.timespan.upper

    def is_relevant(self, booking: Booking, cumulative_revenue="ignored"):
        if booking.stock.offerId == self.offerId:
            return True
        if self.categories:
            sub_category = subcategories.ALL_SUBCATEGORIES_DICT[booking.stock.offer.subcategoryId]
            if sub_category.category_id not in self.categories:
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
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    amount = Column(Numeric(10, 2), nullable=False)

    userId = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)

    user = relationship("User", foreign_keys=[userId], backref="deposits")

    individual_bookings = relationship("IndividualBooking", back_populates="deposit")

    source = Column(String(300), nullable=False)

    dateCreated = Column(DateTime, nullable=False, default=datetime.datetime.utcnow(), server_default=func.now())

    expirationDate = Column(DateTime, nullable=True)

    version = Column(SmallInteger, nullable=False)

    type = Column(
        "type",
        Enum(DepositType, native_enum=False, create_constraint=False),
        nullable=False,
        server_default=DepositType.GRANT_18.value,
    )
