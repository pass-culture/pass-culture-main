from sqlalchemy import text

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


app.app_context().push()


def validate_constraint() -> None:
    # Disabling statement_timeout as we can't know in advance how long it would take
    db.session.execute(text("SET statement_timeout = 0;"))

    db.session.execute(text("COMMIT;"))
    db.session.execute(
        text("""ALTER TABLE collective_offer VALIDATE CONSTRAINT "collective_offer_offererAddressId_fkey" """)
    )

    # According to PostgreSQL, setting such values this way is affecting only the current session
    # but let's be defensive by setting back to the original values
    db.session.execute(text(f"SET statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}"))


if __name__ == "__main__":
    validate_constraint()
