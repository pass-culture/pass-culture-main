"""Add NOT NULL constraint on "invoice.reimbursementPointId" (step 4 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "adeb447a5a8a"
down_revision = "2bf5c49597c0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("invoice_reimbursementPointId_not_null_constraint", table_name="invoice")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "invoice" ADD CONSTRAINT "invoice_reimbursementPointId_not_null_constraint" CHECK ("reimbursementPointId" IS NOT NULL) NOT VALID"""
    )
