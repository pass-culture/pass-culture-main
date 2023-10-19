"""
validate "collective_offer_template_validation_author_fkey" on "collective_offer_template" table 2/2
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8f4c9a84efa0"
down_revision = "64f6f0c48964"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(
        'ALTER TABLE "collective_offer_template" VALIDATE CONSTRAINT "collective_offer_template_validation_author_fkey"'
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
