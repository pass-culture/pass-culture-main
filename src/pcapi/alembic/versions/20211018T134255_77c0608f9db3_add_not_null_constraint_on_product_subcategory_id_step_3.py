"""add_not_null_constraint_on_product_subcategory_id_step_3
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "77c0608f9db3"
down_revision = "d6028fa2c32b"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("product", "subcategoryId", nullable=False)


def downgrade():
    pass
