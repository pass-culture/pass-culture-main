"""Add NOT NULL constraint on "invoice.reimbursementPointId" (step 3 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2bf5c49597c0"
down_revision = "a38dddc95995"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("invoice", "reimbursementPointId", nullable=False)


def downgrade() -> None:
    op.alter_column("invoice", "reimbursementPointId", nullable=True)
