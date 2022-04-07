from contextlib import contextmanager

from pcapi.models import db


@contextmanager
def transaction():  # type: ignore [no-untyped-def]
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
