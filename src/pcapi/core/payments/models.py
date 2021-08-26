import datetime
from decimal import Decimal

import psycopg2.extras
from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from pcapi.core.bookings.models import Booking
from pcapi.models.db import Model


MIN_DATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)
MAX_DATETIME = datetime.datetime(datetime.MAXYEAR, 1, 1)


class ReimbursementRule:
    def is_active(self, booking: Booking) -> bool:
        valid_from = self.valid_from or MIN_DATETIME
        valid_until = self.valid_until or MAX_DATETIME
        return valid_from <= booking.dateUsed < valid_until

    def is_relevant(self, booking: Booking, cumulative_revenue: Decimal) -> bool:
        raise NotImplementedError()

    @property
    def rate(self) -> Decimal:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        raise NotImplementedError()

    def apply(self, booking: Booking) -> Decimal:
        return Decimal(booking.total_amount * self.rate)


class CustomReimbursementRule(ReimbursementRule, Model):
    """Some offers are linked to custom reimbursement rules that overrides
    standard reimbursement rules.

    An offer may be linked to more than one reimbursement rules, but
    only one rule can be valid at a time.
    """

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    offerId = Column(BigInteger, ForeignKey("offer.id"), nullable=False)

    offer = relationship("Offer", foreign_keys=[offerId], backref="custom_reimbursement_rules")

    amount = Column(Numeric(10, 2), nullable=False)

    timespan = Column(postgresql.TSRANGE)

    __table_args__ = (
        # No overlapping timespan for any given offer id.
        postgresql.ExcludeConstraint(("offerId", "="), ("timespan", "&&")),
        # A timespan must have a lower bound. Upper bound is optional.
        CheckConstraint("lower(timespan) IS NOT NULL"),
    )

    def __init__(self, **kwargs):
        kwargs["timespan"] = self._make_timespan(*kwargs["timespan"])
        super().__init__(**kwargs)

    @classmethod
    def _make_timespan(cls, start, end=None):
        return psycopg2.extras.DateTimeRange(start.isoformat(), end.isoformat() if end else None, bounds="[)")

    def is_active(self, booking: Booking):
        if booking.dateCreated < self.timespan.lower:
            return False
        return self.timespan.upper is None or booking.dateCreated < self.timespan.upper

    def is_relevant(self, booking: Booking, cumulative_revenue="ignored"):
        return booking.stock.offerId == self.offerId

    def apply(self, booking: Booking):
        return booking.quantity * self.amount

    @property
    def description(self):  # implementation of ReimbursementRule.description
        raise TypeError("A custom reimbursement rule does not have any description")

    @property
    def rate(self):  # implementation of ReimbursementRule.rate
        raise TypeError("A custom reimbursement rule does not have any rate")
