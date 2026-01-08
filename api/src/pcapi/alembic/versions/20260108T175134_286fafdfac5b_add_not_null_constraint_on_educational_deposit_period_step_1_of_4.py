"""Add NOT NULL constraint on "educational_deposit.period" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "286fafdfac5b"
down_revision = "b5302ae5470d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "educational_deposit" DROP CONSTRAINT IF EXISTS "educational_deposit_period_not_null_constraint";
        ALTER TABLE "educational_deposit" ADD CONSTRAINT "educational_deposit_period_not_null_constraint" CHECK ("period" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("educational_deposit_period_not_null_constraint", table_name="educational_deposit")
