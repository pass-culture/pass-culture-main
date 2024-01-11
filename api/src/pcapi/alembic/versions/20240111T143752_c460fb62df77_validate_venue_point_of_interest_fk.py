"""Validate venue.PointOfInterestId FK
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c460fb62df77"
down_revision = "6672bb132441"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(sa.text('ALTER TABLE venue VALIDATE CONSTRAINT "venue_pointOfInterestId_fkey"'))
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    # Nothing to downgrade
    pass
