"""Add NOT NULL constraint on "cashflow.reimbursementPointId" (step 3 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "dbe2c8189c57"
down_revision = "cf081b3140fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("cashflow", "reimbursementPointId", nullable=False)


def downgrade() -> None:
    op.alter_column("cashflow", "reimbursementPointId", nullable=True)
