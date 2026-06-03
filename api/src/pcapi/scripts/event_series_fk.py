import logging

from sqlalchemy import text

from pcapi import settings
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("add_event_series_fk")
def add_event_series_fk() -> None:
    """Safely adds and validates the FK constraint on event_series_offer_link referencing offer."""
    logger.info("Starting script to add and validate FK constraint on event_series_offer_link")

    # We disable statement timeout for long operations
    db.session.execute(text("SET statement_timeout = 0;"))
    db.session.execute(text("COMMIT;"))

    # Add the constraint as NOT VALID
    logger.info("Adding constraint event_series_offer_link_offerId_fkey NOT VALID...")
    db.session.execute(
        text(
            """
            ALTER TABLE "event_series_offer_link"
            ADD CONSTRAINT "event_series_offer_link_offerId_fkey"
            FOREIGN KEY ("offerId") REFERENCES "offer" ("id")
            ON DELETE CASCADE
            NOT VALID;
            """
        )
    )
    db.session.execute(text("COMMIT;"))

    # Validate the constraint
    logger.info("Validating constraint event_series_offer_link_offerId_fkey...")
    db.session.execute(
        text(
            """
            ALTER TABLE "event_series_offer_link"
            VALIDATE CONSTRAINT "event_series_offer_link_offerId_fkey";
            """
        )
    )
    db.session.execute(text("COMMIT;"))

    # Restore statement timeout
    db.session.execute(text(f"SET statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT};"))
    logger.info("FK constraint added and validated successfully!")
