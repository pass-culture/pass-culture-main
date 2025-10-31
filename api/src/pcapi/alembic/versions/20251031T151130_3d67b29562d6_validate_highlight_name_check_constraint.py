"""Validate highlight_name_check constraint"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3d67b29562d6"
down_revision = "864fbd2feb03"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # or more if needed
    op.execute("""ALTER TABLE highlight VALIDATE CONSTRAINT "highlight_name_check" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
