"""Add NOT NULL constraint on "venue.dmsToken" (step 2 of 4)"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e18d97a2e849"
down_revision = "e459fbfe9086"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    # The timeout here has the same value (5 minutes) as `helm upgrade`.
    # If this migration fails, you'll have to execute it manually.
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "venue" VALIDATE CONSTRAINT "venue_dmsToken_not_null_constraint"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade():
    pass
