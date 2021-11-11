"""add_not_null_constraint_on_offer_subcategory_id_step_4
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e2144d8988c1"
down_revision = "1345cc1cffe4"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("subcategory_id_not_null_constraint", table_name="offer")


def downgrade():
    op.execute(
        """
            ALTER TABLE offer ADD CONSTRAINT subcategory_id_not_null_constraint CHECK ("subcategoryId" IS NOT NULL) NOT VALID;
        """
    )
