"""
Add NOT NULL constraint on "address.departmentCode" (step 4 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "60fdd63d8828"
down_revision = "eed8954b8bca"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("address_departmentCode_not_null_constraint", table_name="address")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "address" ADD CONSTRAINT "address_departmentCode_not_null_constraint" CHECK ("departmentCode" IS NOT NULL) NOT VALID"""
    )
