"""add_not_null_constraint_on_offer_subcategory_id_step_3
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "1345cc1cffe4"
down_revision = "e2144d8988c1"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("offer", "subcategoryId", nullable=False)


def downgrade():
    pass
