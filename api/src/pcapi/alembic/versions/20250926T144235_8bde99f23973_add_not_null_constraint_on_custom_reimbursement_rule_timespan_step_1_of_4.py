"""Add NOT NULL constraint on "custom_reimbursement_rule.timespan" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8bde99f23973"
down_revision = "bd6e1c75b3eb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "custom_reimbursement_rule" DROP CONSTRAINT IF EXISTS "custom_reimbursement_rule_timespan_not_null_constraint";
        ALTER TABLE "custom_reimbursement_rule" ADD CONSTRAINT "custom_reimbursement_rule_timespan_not_null_constraint" CHECK ("timespan" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("custom_reimbursement_rule_timespan_not_null_constraint", table_name="custom_reimbursement_rule")
