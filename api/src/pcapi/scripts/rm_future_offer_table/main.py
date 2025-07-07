import sqlalchemy as sa

from pcapi import settings
from pcapi.models import db


def run() -> None:
    db.session.execute(sa.text("SET SESSION statement_timeout = '300s'"))
    db.session.execute(sa.text("DROP TABLE IF EXISTS future_offer"))
    db.session.execute(sa.text(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))
