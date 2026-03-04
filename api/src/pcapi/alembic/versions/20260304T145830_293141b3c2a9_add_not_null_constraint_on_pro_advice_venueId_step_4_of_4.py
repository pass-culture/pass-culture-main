"""Add NOT NULL constraint on "pro_advice.venueId" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "293141b3c2a9"
down_revision = "ccc59658611d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("pro_advice_venueId_not_null_constraint", table_name="pro_advice")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "pro_advice" ADD CONSTRAINT "pro_advice_venueId_not_null_constraint" CHECK ("venueId" IS NOT NULL) NOT VALID"""
    )
