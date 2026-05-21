import logging
import typing
from contextlib import contextmanager

from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import is_managed_transaction


logger = logging.getLogger(__name__)


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
