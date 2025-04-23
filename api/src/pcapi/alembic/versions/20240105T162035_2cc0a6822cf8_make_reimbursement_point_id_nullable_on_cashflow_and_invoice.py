"""Make "reimbursementPointId" nullable in "cashflow" and "invoice" tables"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2cc0a6822cf8"
down_revision = "fadf7f6f4c60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("cashflow", "reimbursementPointId", existing_type=sa.BIGINT(), nullable=True)
    op.alter_column("invoice", "reimbursementPointId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    op.alter_column("invoice", "reimbursementPointId", existing_type=sa.BIGINT(), nullable=False)
    op.alter_column("cashflow", "reimbursementPointId", existing_type=sa.BIGINT(), nullable=False)
