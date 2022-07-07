import psycopg2.errors
import sqlalchemy as sqla
import sqlalchemy.exc as sqla_exc

from pcapi.models import Base
from pcapi.models import Model

from . import exceptions


class ReferenceScheme(Base, Model):  # type: ignore [valid-type, misc]
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

    id = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    # known names and prefixes are:
    #   - invoice.reference: F
    name = sqla.Column(sqla.Text, nullable=False)
    prefix = sqla.Column(sqla.Text, nullable=False)
    year = sqla.Column(sqla.Integer)
    nextNumber = sqla.Column(sqla.Integer, default=1)
    numberPadding = sqla.Column(sqla.Integer, default=7)

    __table_args__ = (
        sqla.UniqueConstraint(
            "name",
            "year",
            name="unique_name_year",
        ),
        sqla.UniqueConstraint(
            "prefix",
            "year",
            name="unique_prefix_year",
        ),
    )

    @classmethod
    def get_and_lock(cls, name, year=None):  # type: ignore [no-untyped-def]
        # Here we wait for the lock. If another transaction has a
        # lock, that's fine: we'll wait for that other transaction to
        # commit and release the lock, so that we get the latest,
        # updated reference.
        return (
            cls.query.populate_existing()
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
        except sqla_exc.OperationalError as exc:
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
