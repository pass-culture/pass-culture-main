"""add_not_null_constraint_on_product_subcategory_id_step_1
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "00da19d9eaae"
down_revision = "1345cc1cffe4"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE product DROP CONSTRAINT IF EXISTS subcategory_id_not_null_constraint;
            ALTER TABLE product ADD CONSTRAINT subcategory_id_not_null_constraint  CHECK ("subcategoryId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("subcategory_id_not_null_constraint", table_name="product")
