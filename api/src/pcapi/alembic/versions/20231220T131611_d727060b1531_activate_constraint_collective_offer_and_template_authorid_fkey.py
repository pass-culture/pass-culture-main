"""
Validate constraint in collective_offer and collective_offer_template (authorId_fkey)
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d727060b1531"
down_revision = "faed981725fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE collective_offer_template VALIDATE CONSTRAINT "collective_offer_template_authorId_fkey"')
    op.execute('ALTER TABLE collective_offer VALIDATE CONSTRAINT "collective_offer_authorId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
