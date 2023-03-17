"""Drop `user.hasCompletedIdCheck` column"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9b02e53e8369"
down_revision = "8eb478cb4014"
branch_labels = None
depends_on = None


def upgrade():
    # Increase default timeout, because the table is frequently used
    # and we are thus likely to wait before acquiring the lock that is
    # necessary to drop the column.
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS "hasCompletedIdCheck"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade():
    pass  # The column is not used, there is no point in adding it back.
