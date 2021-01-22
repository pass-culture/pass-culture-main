"""add_not_null_stock_date_created_step_1 (Add not null constraint to stock.dateCreated: Step 1/4)

Revision ID: e8795c007a78
Revises: 0e2e82aa2d40
Create Date: 2021-01-22 15:40:22.518190

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e8795c007a78"
down_revision = "0e2e82aa2d40"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE stock ADD CONSTRAINT stock_date_created_not_null_constraint CHECK ("dateCreated" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("stock_date_created_not_null_constraint", table_name="stock")
