"""add_not_null_product_gcu_step_2 (Add not null constraint to product.isGcuCompatible: Step 2/4)

Revision ID: a5ce113f696d
Revises: 44266d101920
Create Date: 2021-01-25 16:41:09.325686

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "a5ce113f696d"
down_revision = "44266d101920"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE product VALIDATE CONSTRAINT product_is_gcu_not_null_constraint;")


def downgrade():
    pass
