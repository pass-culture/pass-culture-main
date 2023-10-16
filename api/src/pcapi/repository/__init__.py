from contextlib import contextmanager
from typing import Iterator

from pcapi.models import db


@contextmanager
def transaction() -> Iterator[None]:
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
