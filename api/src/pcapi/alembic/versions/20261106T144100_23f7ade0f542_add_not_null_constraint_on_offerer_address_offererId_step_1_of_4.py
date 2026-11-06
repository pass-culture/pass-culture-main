"""Add NOT NULL constraint on "offerer_address.offererId" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "23f7ade0f542"
down_revision = "07f33b4d4b2e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "offerer_address" DROP CONSTRAINT IF EXISTS "offerer_address_offererId_not_null_constraint";
        ALTER TABLE "offerer_address" ADD CONSTRAINT "offerer_address_offererId_not_null_constraint" CHECK ("offererId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("offerer_address_offererId_not_null_constraint", table_name="offerer_address")
