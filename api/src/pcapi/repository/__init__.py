import typing
from contextlib import contextmanager

from pcapi.models import db

from . import session_management


# DEPRECATED in favor of @atomic() because @transaction() is not reentrant
@contextmanager
def transaction() -> typing.Iterator[None]:
    if session_management.is_managed_transaction():
        with session_management.atomic():
            yield
    else:
        try:
            yield
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
