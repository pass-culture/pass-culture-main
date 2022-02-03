"""Rename invoice_line columns"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b400b5a91243"
down_revision = "b76548e8af14"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("invoice_line", "reimbursed_amount", new_column_name="reimbursedAmount")
    op.alter_column("invoice_line", "contribution_amount", new_column_name="contributionAmount")


def downgrade():
    op.alter_column("invoice_line", "reimbursedAmount", new_column_name="reimbursed_amount")
    op.alter_column("invoice_line", "contributionAmount", new_column_name="contribution_amount")
