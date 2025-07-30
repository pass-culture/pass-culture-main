"""Validate constraint check_credit_ratio_is_a_percentage"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "abac82d96860"
down_revision = "e1a6f2f354b8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE educational_deposit VALIDATE CONSTRAINT "check_credit_ratio_is_a_percentage" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
