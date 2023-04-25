"""provider_api_key: validate provider_id foreign key constraint (3/3)
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8a69ae7f952e"
down_revision = "00d3b5d28578"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "api_key" VALIDATE CONSTRAINT "api_key_providerId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
