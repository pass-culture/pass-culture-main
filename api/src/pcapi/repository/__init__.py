from contextlib import contextmanager
import typing

from pcapi.models import db

# TODO: remove once all the call to this module hav been modified to call sessionmanager
from .session_management import _manage_session
from .session_management import _mark_session_management
from .session_management import atomic
from .session_management import is_managed_transaction
from .session_management import mark_transaction_as_invalid
from .session_management import on_commit


# DEPRECATED in favor of @atomic() because @transaction() is not reentrant
@contextmanager
def transaction() -> typing.Iterator[None]:
    if is_managed_transaction():
        with atomic():
            yield
    else:
        try:
            yield
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
