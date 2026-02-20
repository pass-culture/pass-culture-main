"""Add NOT NULL constraint on "offererAddress.type" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1d26ab58b9c0"
down_revision = "f1ee85f969b0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "offerer_address" VALIDATE CONSTRAINT "offererAddress_type_not_null_constraint"')
        op.execute('ALTER TABLE "offerer_address" VALIDATE CONSTRAINT "offererAddress_venueId_not_null_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
