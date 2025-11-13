"""Add NOT NULL constraint on "educational_deposit.ministry" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5c8418f46c80"
down_revision = "bff3f0e86268"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("educational_deposit_ministry_not_null_constraint", table_name="educational_deposit")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "educational_deposit" ADD CONSTRAINT "educational_deposit_ministry_not_null_constraint" CHECK ("ministry" IS NOT NULL) NOT VALID"""
    )
