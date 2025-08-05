import typing
from contextlib import contextmanager

from pcapi.models import db

from ..utils import transaction_manager


# DEPRECATED in favor of @atomic() because @transaction() is not reentrant
@contextmanager
def transaction() -> typing.Iterator[None]:
    if transaction_manager.is_managed_transaction():
        with transaction_manager.atomic():
            yield
    else:
        try:
            yield
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
