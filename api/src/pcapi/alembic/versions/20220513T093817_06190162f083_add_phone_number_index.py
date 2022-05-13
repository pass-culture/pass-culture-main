"""add_phone_number_index
"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "06190162f083"
down_revision = "beaefcf60bc9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_user_phoneNumber" ON "user" ("phoneNumber")
        """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_user_phoneNumber;")
