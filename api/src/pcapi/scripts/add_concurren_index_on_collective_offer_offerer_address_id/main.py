from sqlalchemy import text

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


app.app_context().push()


def add_index() -> None:
    # Disabling statement_timeout as we can't know in advance how long it would take
    db.session.execute(text("SET statement_timeout = 0;"))

    # The below statement can't run inside a transaction
    db.session.execute(text("COMMIT;"))
    db.session.execute(
        text(
            """ CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_collective_offer_offererAddressId" ON collective_offer ("offererAddressId"); """
        )
    )

    # According to PostgreSQL, setting such values this way is affecting only the current session
    # but let's be defensive by setting back to the original values
    db.session.execute(text(f"SET statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}"))


if __name__ == "__main__":
    add_index()
