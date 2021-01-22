"""add_not_null_stock_date_created_step_3 (Add not null constraint to stock.dateCreated: Step 3/4)

Revision ID: 90eed7ed7e7c
Revises: 9f7d90d58760
Create Date: 2021-01-22 15:40:30.148375

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "90eed7ed7e7c"
down_revision = "9f7d90d58760"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("stock", "dateCreated", nullable=False)


def downgrade():
    op.alter_column("stock", "dateCreated", nullable=True)
