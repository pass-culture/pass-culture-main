"""add_not_null_stock_date_created_step_2 (Add not null constraint to stock.dateCreated: Step 2/4)

Revision ID: 9f7d90d58760
Revises: e8795c007a78
Create Date: 2021-01-22 15:40:26.071442

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9f7d90d58760"
down_revision = "e8795c007a78"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE stock VALIDATE CONSTRAINT stock_date_created_not_null_constraint;")


def downgrade():
    pass
