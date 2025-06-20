"""Validate action_history constraints"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "59ae58ae19c8"
down_revision = "902bdb2449b9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE action_history VALIDATE CONSTRAINT "check_action_resource" """)
    op.execute("""ALTER TABLE action_history VALIDATE CONSTRAINT "action_history_noticeId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
