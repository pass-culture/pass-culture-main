"""Validate previously added OffererPointofInterest.OffererId FK
"""
from alembic import op
import sqlalchemy as sa
from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7e365d8d301b"
down_revision = "d4d4d6006520"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute(
        sa.text(
            """ALTER TABLE offerer_point_of_interest VALIDATE CONSTRAINT "offerer_point_of_interest_offererId_fkey";"""
        ),
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    # Nothing to downgrade
    pass
