"""
Add NOT NULL constraint on "offerer_address.offererId" and "offerer_address.addressId" (step 2 of 4)
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "eaeb8cfda46d"
down_revision = "6a98ca9d012f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "offerer_address" VALIDATE CONSTRAINT "offerer_address_offererId_not_null_constraint"')
        op.execute('ALTER TABLE "offerer_address" VALIDATE CONSTRAINT "offerer_address_addressId_not_null_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
