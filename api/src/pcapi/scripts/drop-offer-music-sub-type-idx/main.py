from sqlalchemy import text

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


app.app_context().push()


def drop_index() -> None:
    # Disabling statement_timeout as we know it's gonna take a while
    db.session.execute(text("SET statement_timeout = 0;"))

    # The below statement can't run inside a transaction
    db.session.execute(text("COMMIT;"))
    db.session.execute(text(""" DROP INDEX CONCURRENTLY "offer_music_sub_type_idx"; """))
    db.session.execute(text(f"SET statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}"))


if __name__ == "__main__":
    drop_index()
