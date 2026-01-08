"""Add NOT NULL constraint on "educational_deposit.period" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bba150bb6dab"
down_revision = "a2eac7fc5bac"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("educational_deposit_period_not_null_constraint", table_name="educational_deposit")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "educational_deposit" ADD CONSTRAINT "educational_deposit_period_not_null_constraint" CHECK ("period" IS NOT NULL) NOT VALID"""
    )
