"""Add NOT NULL constraint on "custom_reimbursement_rule.timespan" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3e9544462f05"
down_revision = "67857efc0589"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("custom_reimbursement_rule_timespan_not_null_constraint", table_name="custom_reimbursement_rule")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "custom_reimbursement_rule" ADD CONSTRAINT "custom_reimbursement_rule_timespan_not_null_constraint" CHECK ("timespan" IS NOT NULL) NOT VALID"""
    )
