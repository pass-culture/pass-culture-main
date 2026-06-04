"""Add foreign key constraint on event_series_offer_link.offerId"""

import logging

import sqlalchemy as sa
from alembic import context
from alembic import op

from pcapi import settings


logger = logging.getLogger("alembic.runtime.migration")

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "042ffc4e412b"
down_revision = "ad37625d13c0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def check_if_constraint_exists() -> bool:
    """
    Check if the constraint already exists.
    In offline mode, we return False as we can't check.
    """
    if context.is_offline_mode():
        return False

    connection = op.get_bind()
    query = sa.text(
        "SELECT convalidated FROM pg_constraint WHERE conname = 'event_series_offer_link_offerId_fkey' AND conrelid = CAST('event_series_offer_link' AS regclass)"
    )
    result = connection.execute(query).first()
    return result is not None


def upgrade() -> None:

    constraint_already_exists = check_if_constraint_exists()

    if not constraint_already_exists:  # Create constraint if not exists
        logger.warning("Creating constraint event_series_offer_link_offerId_fkey NOT VALID...")
        op.create_foreign_key(
            "event_series_offer_link_offerId_fkey",
            "event_series_offer_link",
            "offer",
            ["offerId"],
            ["id"],
            ondelete="CASCADE",
            postgresql_not_valid=True,
        )
    else:
        logger.warning("Constraint event_series_offer_link_offerId_fkey already exists, skipping creation")

    # In both cases, we validate the constraint
    op.execute("COMMIT")
    op.execute("BEGIN")
    op.execute('SET SESSION statement_timeout = "300s"')
    op.execute('ALTER TABLE "event_series_offer_link" VALIDATE CONSTRAINT "event_series_offer_link_offerId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.drop_constraint(
        "event_series_offer_link_offerId_fkey",
        "event_series_offer_link",
        type_="foreignkey",
    )
