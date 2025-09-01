"""
https://github.com/pass-culture/pass-culture-main/blob/pc-37607/script-index-achievement-booking-id-foreign-key/api/src/pcapi/scripts/index_achievement_booking_id/main.py

"""

import logging

from sqlalchemy import text

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    with db.engine.begin() as connection:
        connection.execute(text("COMMIT"))
        connection.execute(text("SET SESSION statement_timeout='300s'"))
        connection.execute(
            text(
                'CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_achievement_bookingId" ON achievement USING btree ("bookingId")'
            )
        )
        connection.execute(text(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))


if __name__ == "__main__":
    app.app_context().push()

    main()
