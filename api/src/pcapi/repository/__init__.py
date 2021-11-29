from contextlib import contextmanager

from pcapi.models import db


@contextmanager
def transaction():
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
