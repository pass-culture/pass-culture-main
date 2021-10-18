"""add_not_null_constraint_on_product_subcategory_id_step_4
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "d65f31d992fa"
down_revision = "77c0608f9db3"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("subcategory_id_not_null_constraint", table_name="product")


def downgrade():
    op.execute(
        """
            ALTER TABLE product ADD CONSTRAINT subcategory_id_not_null_constraint CHECK ("subcategoryId" IS NOT NULL) NOT VALID;
        """
    )
