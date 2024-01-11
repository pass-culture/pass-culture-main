"""Validate offer.PointOfInterestId fk
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "757ce6c389fd"
down_revision = "c2508ddfe52b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(sa.text('ALTER TABLE offer VALIDATE CONSTRAINT "offer_pointOfInterestId_fkey"'))
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    # Nothing to downgrade
    pass
