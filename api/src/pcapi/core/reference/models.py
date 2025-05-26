import logging

import psycopg2.errors
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc

from pcapi import settings
from pcapi.core.logging import log_elapsed
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db

from . import exceptions


logger = logging.getLogger(__name__)


class ReferenceScheme(Base, Model):
    """This table holds the next reference number (and other related
    parameters) for our invoices and possibly other entities.

    The goal is to have a way to generate consecutive reference
    numbers without gaps. We cannot use a serial sequence, because
    transaction rollbacks do not "decrease" the sequence and that
    would cause a gap. Instead, we store the next reference in a row
    of this table and update it only within the same transaction that
    sets that reference on the related entity (e.g. ``invoice``).

    Usage:

        scheme = models.ReferenceScheme.get_and_lock(name="invoice.reference", year=year)
        invoice.reference = scheme.formatted_reference
        scheme.increment_after_use()
        db.session.add(invoice)
        db.session.add(scheme)
        db.session.commit()

    It is very important that there is a single transaction that
    encloses all calls. If a transaction commits the use of the
    reference model and another transaction commits the
    incrementation, there is a risk that the latter fails because a
    lock was taken in the meantime, and also that the same reference
    was used twice.
    """

    __tablename__ = "reference_scheme"
    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    # known names and prefixes are:
    #   - invoice.reference: F
    #   - debit_note.reference: A
    name: str = sa.Column(sa.Text, nullable=False)
    prefix: str = sa.Column(sa.Text, nullable=False)
    year = sa.Column(sa.Integer)
    nextNumber = sa.Column(sa.Integer, default=1)
    numberPadding = sa.Column(sa.Integer, default=7)

    __table_args__ = (
        sa.UniqueConstraint(
            "name",
            "year",
            name="unique_name_year",
        ),
        sa.UniqueConstraint(
            "prefix",
            "year",
            name="unique_prefix_year",
        ),
    )

    @classmethod
    def get_and_lock(cls, name: str, year: int | None = None) -> "ReferenceScheme":
        # Here we wait for the lock. If another transaction has a
        # lock, that's fine: we'll wait for that other transaction to
        # commit and release the lock, so that we get the latest,
        # updated reference.
        with log_elapsed(logger, "Waited to acquire lock to update ReferenceScheme"):
            return (
                db.session.query(cls)
                .populate_existing()
                .with_for_update(nowait=False)
                .filter_by(
                    name=name,
                    year=year,
                )
                .one()
            )

    def increment_after_use(self) -> None:
        # Here we do NOT wait for the lock to be available. If we're
        # trying to increment the reference while it's being locked by
        # another transaction, it means that the current code path did
        # NOT lock it in the first place. As such, it's possible that
        # we did not get the latest reference, and hence we should
        # fail now. It could indicate a bug.
        try:
            self.query.with_for_update(nowait=True).filter_by(id=self.id).update(
                {"nextNumber": ReferenceScheme.nextNumber + 1}
            )
        except sa_exc.OperationalError as exc:
            if isinstance(exc.orig, psycopg2.errors.LockNotAvailable):
                msg = f"Could not acquire lock on reference {self.id}"
                raise exceptions.ReferenceIncrementWithoutLock(msg) from exc
            raise exc

    def reset_next_number(self) -> None:
        if not settings.IS_RUNNING_TESTS:
            raise ValueError("Reference next number sequence can only be reset in tests")
        try:
            self.query.with_for_update(nowait=True).filter_by(id=self.id).update({"nextNumber": 1})
        except sa_exc.OperationalError as exc:
            if isinstance(exc.orig, psycopg2.errors.LockNotAvailable):
                msg = f"Could not acquire lock on reference {self.id}"
                raise exceptions.ReferenceIncrementWithoutLock(msg) from exc
            raise exc

    @property
    def formatted_reference(self) -> str:
        # e.g. "F230000001" or "X0001"
        # fmt: off
        return (
            f"{self.prefix}"
            f"{self.year % 2000 if self.year else ''}"
            f"{self.nextNumber:0{self.numberPadding}}"
        )
        # fmt: on
