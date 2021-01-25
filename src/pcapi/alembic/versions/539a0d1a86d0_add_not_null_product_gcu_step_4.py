"""add_not_null_product_gcu_step_4 (Add not null constraint to product.isGcuCompatible: Step 4/4)

Revision ID: 539a0d1a86d0
Revises: c992abf72832
Create Date: 2021-01-25 16:41:16.546239

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "539a0d1a86d0"
down_revision = "c992abf72832"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("product_is_gcu_not_null_constraint", table_name="product")


def downgrade():
    op.execute(
        """
            ALTER TABLE product ADD CONSTRAINT product_is_gcu_not_null_constraint CHECK ("isGcuCompatible" IS NOT NULL) NOT VALID;
        """
    )
