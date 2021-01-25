"""add_not_null_product_gcu_step_3 (Add not null constraint to product.isGcuCompatible: Step 3/4)

Revision ID: c992abf72832
Revises: a5ce113f696d
Create Date: 2021-01-25 16:41:13.199217

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c992abf72832"
down_revision = "a5ce113f696d"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("product", "isGcuCompatible", nullable=False)


def downgrade():
    op.alter_column("product", "isGcuCompatible", nullable=True)
