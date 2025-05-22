"""
Add NOT NULL constraint on "offerer_address.offererId" and "offerer_address.addressId" (step 4 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cf1495e11a53"
down_revision = "31027ffad5ad"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("offerer_address_offererId_not_null_constraint", table_name="offerer_address")
    op.drop_constraint("offerer_address_addressId_not_null_constraint", table_name="offerer_address")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "offerer_address" ADD CONSTRAINT "offerer_address_offererId_not_null_constraint" CHECK ("offererId" IS NOT NULL) NOT VALID"""
    )
    op.execute(
        """ALTER TABLE "offerer_address" ADD CONSTRAINT "offerer_address_addressId_not_null_constraint" CHECK ("addressId" IS NOT NULL) NOT VALID"""
    )
