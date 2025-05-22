"""Add NOT NULL constraint on "address.street" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1ad10f56b216"
down_revision = "f7a60b79eabd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "address" DROP CONSTRAINT IF EXISTS "address_street_not_null_constraint";
        ALTER TABLE "address" ADD CONSTRAINT "address_street_not_null_constraint" CHECK ("street" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("address_street_not_null_constraint", table_name="address")
