"""
Add NOT NULL constraint on "headline_offer.timespan" (step 2 of 4)
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c125573195bc"
down_revision = "e9e2d200017f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "headline_offer" VALIDATE CONSTRAINT "timespan_not_null_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS timespan_not_null_constraint")
