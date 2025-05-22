"""
Add NOT NULL constraint on "offerer_address.offererId" and "offerer_address.addressId" (step 1 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6a98ca9d012f"
down_revision = "d01d0e1ad810"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "offerer_address" DROP CONSTRAINT IF EXISTS "offerer_address_offererId_not_null_constraint";
        ALTER TABLE "offerer_address" ADD CONSTRAINT "offerer_address_offererId_not_null_constraint" CHECK ("offererId" IS NOT NULL) NOT VALID;
        """
    )
    op.execute(
        """
        ALTER TABLE "offerer_address" DROP CONSTRAINT IF EXISTS "offerer_address_addressId_not_null_constraint";
        ALTER TABLE "offerer_address" ADD CONSTRAINT "offerer_address_addressId_not_null_constraint" CHECK ("addressId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("offerer_address_offererId_not_null_constraint", table_name="offerer_address")
    op.drop_constraint("offerer_address_addressId_not_null_constraint", table_name="offerer_address")
