"""Set mediation.authorId as null when user is deleted 2/2
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a09a9a890bcb"
down_revision = "d968ffd57c40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE mediation VALIDATE CONSTRAINT "mediation_authorId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
