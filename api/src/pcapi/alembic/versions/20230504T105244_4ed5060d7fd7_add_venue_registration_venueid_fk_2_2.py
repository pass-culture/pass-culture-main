"""Add venue_registration venueId FK 2/2
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4ed5060d7fd7"
down_revision = "e6452b3c197d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "venue_registration" VALIDATE CONSTRAINT "venue_registration_venueId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
