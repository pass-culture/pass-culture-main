"""Add `venue.timezone`
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "69ef0222cdc8"
down_revision = "dcfd7657a244"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.add_column("venue", sa.Column("timezone", sa.String(length=50), server_default="Europe/Paris", nullable=False))
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.drop_column("venue", "timezone")
