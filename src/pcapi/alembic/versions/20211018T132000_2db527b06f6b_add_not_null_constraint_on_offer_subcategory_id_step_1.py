"""add_not_null_constraint_on_offer_subcategory_id_step_1
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2db527b06f6b"
down_revision = "25ed998d46e8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE offer DROP CONSTRAINT IF EXISTS subcategory_id_not_null_constraint;
            ALTER TABLE offer ADD CONSTRAINT subcategory_id_not_null_constraint CHECK ("subcategoryId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("subcategory_id_not_null_constraint", table_name="offer")
