"""Validate achievements constraints"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "43fee1eab19d"
down_revision = "53e2600b8585"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE achievement VALIDATE CONSTRAINT "achievement_userId_fkey" """)
    op.execute("""ALTER TABLE achievement VALIDATE CONSTRAINT "achievement_bookingId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
