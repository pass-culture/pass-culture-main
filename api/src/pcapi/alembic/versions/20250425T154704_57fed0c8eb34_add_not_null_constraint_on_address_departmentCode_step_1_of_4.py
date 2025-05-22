"""
Add NOT NULL constraint on "address.departmentCode" (step 1 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "57fed0c8eb34"
down_revision = "e9cf3954ed3b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "address" DROP CONSTRAINT IF EXISTS "address_departmentCode_not_null_constraint";
        ALTER TABLE "address" ADD CONSTRAINT "address_departmentCode_not_null_constraint" CHECK ("departmentCode" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("address_departmentCode_not_null_constraint", table_name="address")
