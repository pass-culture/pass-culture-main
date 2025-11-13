"""Add NOT NULL constraint on "educational_deposit.ministry" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "93859aacbfe4"
down_revision = "d762cbe269af"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "educational_deposit" DROP CONSTRAINT IF EXISTS "educational_deposit_ministry_not_null_constraint";
        ALTER TABLE "educational_deposit" ADD CONSTRAINT "educational_deposit_ministry_not_null_constraint" CHECK ("ministry" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("educational_deposit_ministry_not_null_constraint", table_name="educational_deposit")
