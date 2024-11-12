import argparse
import logging

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()


def reindexing() -> None:
    db.session.execute("COMMIT;")
    db.session.execute(sa.text("""SET SESSION statement_timeout = '2600s' ;"""))
    db.session.execute(sa.text("""REINDEX INDEX CONCURRENTLY ix_unique_offerer_address_per_label ;"""))
    db.session.execute(
        sa.text("""SET SESSION statement_timeout = :timeout ;"""), {"timeout": settings.DATABASE_STATEMENT_TIMEOUT}
    )

    db.session.execute("BEGIN;")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Default parser")
    args = parser.parse_args()

    try:
        reindexing()
    except:
        db.session.rollback()
        raise
