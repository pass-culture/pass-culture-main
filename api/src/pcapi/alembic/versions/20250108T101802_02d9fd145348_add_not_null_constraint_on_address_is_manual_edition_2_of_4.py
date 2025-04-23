"""Add NOT NULL constraint on address."isManualEdition" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "02d9fd145348"
down_revision = "fa316a36cbcc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "address" VALIDATE CONSTRAINT "is_manual_edition_not_null_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("ALTER TABLE address DROP CONSTRAINT IF EXISTS is_manual_edition_not_null_constraint")
