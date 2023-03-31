"""Add NOT NULL constraint on "invoice.reimbursementPointId" (step 1 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e1c94058cc97"
down_revision = "93a4f804768a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "invoice" DROP CONSTRAINT IF EXISTS "invoice_reimbursementPointId_not_null_constraint";
        ALTER TABLE "invoice" ADD CONSTRAINT "invoice_reimbursementPointId_not_null_constraint" CHECK ("reimbursementPointId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("invoice_reimbursementPointId_not_null_constraint", table_name="invoice")
