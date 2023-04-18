"""offerer_provider : validate offerer_provider_offererId_fkey (step 6 of 6)
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7e3cb87c42ec"
down_revision = "e9c5ec411702"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "offerer_provider" VALIDATE CONSTRAINT "offerer_provider_offererId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
