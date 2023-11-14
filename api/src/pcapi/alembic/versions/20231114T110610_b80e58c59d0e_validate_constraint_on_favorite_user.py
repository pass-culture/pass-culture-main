"""Delete favorites when user is deleted 2/2
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b80e58c59d0e"
down_revision = "6e7c61f3c36f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE favorite VALIDATE CONSTRAINT "favorite_userId_fkey"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
