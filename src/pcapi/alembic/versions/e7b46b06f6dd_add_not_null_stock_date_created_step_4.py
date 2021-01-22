"""add_not_null_stock_date_created_step_4 (Add not null constraint to stock.dateCreated: Step 4/4)

Revision ID: e7b46b06f6dd
Revises: 90eed7ed7e7c
Create Date: 2021-01-22 15:40:34.079071

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e7b46b06f6dd"
down_revision = "90eed7ed7e7c"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("stock_date_created_not_null_constraint", table_name="stock")


def downgrade():
    op.execute(
        """
            ALTER TABLE stock ADD CONSTRAINT stock_date_created_not_null_constraint CHECK ("dateCreated" IS NOT NULL) NOT VALID;
        """
    )
