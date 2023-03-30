"""Add pro_user_flags_userId_fkey (step 2/2)"""
from alembic import op
from alembic.runtime.migration import log

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "580466424daf"
down_revision = "841f91f7e665"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    # The timeout here has the same value (5 minutes) as `helm upgrade`.
    log.info(">>> HINT: If this migration fails, you'll have to execute it manually from a pgcli console")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "user_pro_flags" VALIDATE CONSTRAINT "user_pro_flags_userId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
