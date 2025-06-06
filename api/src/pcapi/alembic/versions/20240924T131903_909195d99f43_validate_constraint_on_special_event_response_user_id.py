"""Validate constraint on special_event_response.userId"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "909195d99f43"
down_revision = "e76deb66bf86"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute("""ALTER TABLE special_event_response VALIDATE CONSTRAINT "special_event_response_userId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
