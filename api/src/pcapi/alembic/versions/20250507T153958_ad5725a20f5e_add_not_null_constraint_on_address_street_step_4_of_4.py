"""Add NOT NULL constraint on "address.street" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ad5725a20f5e"
down_revision = "2957c0896d6d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("address_street_not_null_constraint", table_name="address")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "address" ADD CONSTRAINT "address_street_not_null_constraint" CHECK ("street" IS NOT NULL) NOT VALID"""
    )
