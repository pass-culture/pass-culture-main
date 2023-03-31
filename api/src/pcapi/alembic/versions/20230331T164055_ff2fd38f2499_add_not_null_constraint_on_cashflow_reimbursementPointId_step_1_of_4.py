"""Add NOT NULL constraint on "cashflow.reimbursementPointId" (step 1 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ff2fd38f2499"
down_revision = "da9509688eb1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "cashflow" DROP CONSTRAINT IF EXISTS "cashflow_reimbursementPointId_not_null_constraint";
        ALTER TABLE "cashflow" ADD CONSTRAINT "cashflow_reimbursementPointId_not_null_constraint" CHECK ("reimbursementPointId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("cashflow_reimbursementPointId_not_null_constraint", table_name="cashflow")
