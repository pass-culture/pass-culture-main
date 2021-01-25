"""add_not_null_product_gcu_step_1 (Add not null constraint to product.isGcuCompatible: Step 1/4)

Revision ID: 44266d101920
Revises: e7b46b06f6dd
Create Date: 2021-01-22 15:40:22.518190

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "44266d101920"
down_revision = "e7b46b06f6dd"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE product ADD CONSTRAINT product_is_gcu_not_null_constraint CHECK ("isGcuCompatible" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("product_is_gcu_not_null_constraint", table_name="product")
