"""Add NOT NULL constraint on "cashflow.reimbursementPointId" (step 4 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "93a4f804768a"
down_revision = "dbe2c8189c57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("cashflow_reimbursementPointId_not_null_constraint", table_name="cashflow")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "cashflow" ADD CONSTRAINT "cashflow_reimbursementPointId_not_null_constraint" CHECK ("reimbursementPointId" IS NOT NULL) NOT VALID"""
    )
