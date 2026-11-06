"""Add NOT NULL constraint on "offerer_address.offererId" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = '2b8c01f25441'
down_revision = '23f7ade0f542'
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "offerer_address" VALIDATE CONSTRAINT "offerer_address_offererId_not_null_constraint"')
        op.execute(
            (f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))


def downgrade() -> None:
    pass
