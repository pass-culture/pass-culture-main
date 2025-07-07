import psycopg2
import pytest
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc

from pcapi.models import db
from pcapi.scripts.rm_future_offer_table.main import run


pytestmark = pytest.mark.usefixtures("db_session")


def is_undefined_table(err):
    try:
        return isinstance(err.orig, psycopg2.errors.UndefinedTable)
    except Exception:
        return False


def test_run():
    run()

    with pytest.raises(sa_exc.ProgrammingError, check=is_undefined_table):
        query = "SELECT * FROM future_offer limit 1"
        db.session.execute(sa.text(query)).all()
