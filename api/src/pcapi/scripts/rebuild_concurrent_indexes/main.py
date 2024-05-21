from sqlalchemy import text

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


def rebuild_concurrent_index() -> None:
    with app.app_context():
        db.session.execute("SET statement_timeout = 0;")  # disable, as we can't know how much it will take
        # Below concurrent queries won't run inside a transaction
        db.session.execute("COMMIT")
        # https://www.postgresql.org/docs/15/sql-reindex.html
        db.session.execute(text("""REINDEX INDEX CONCURRENTLY "ix_offer_criterion_criterionId" """))
        db.session.execute(f"SET statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}")


if __name__ == "__main__":
    rebuild_concurrent_index()
