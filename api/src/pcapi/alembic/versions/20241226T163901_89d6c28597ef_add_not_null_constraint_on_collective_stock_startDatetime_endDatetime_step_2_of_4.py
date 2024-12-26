"""
Add NOT NULL constraint on "collective_stock.startDatetime" and "collective_stock.endDatetime" (step 2 of 4)
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "89d6c28597ef"
down_revision = "a09ff41c9e94"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute(
            'ALTER TABLE "collective_stock" VALIDATE CONSTRAINT "collective_stock_startDatetime_not_null_constraint"'
        )
        op.execute(
            'ALTER TABLE "collective_stock" VALIDATE CONSTRAINT "collective_stock_endDatetime_not_null_constraint"'
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
