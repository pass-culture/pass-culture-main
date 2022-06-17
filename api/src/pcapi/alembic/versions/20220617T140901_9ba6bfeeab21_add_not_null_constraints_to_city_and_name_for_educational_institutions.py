"""add_not_null_constraints_to_city_and_name_for_educational_institutions
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9ba6bfeeab21"
down_revision = "e6159681454f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("educational_institution", "city", existing_type=sa.TEXT(), nullable=False)
    op.alter_column("educational_institution", "name", existing_type=sa.TEXT(), nullable=False)


def downgrade() -> None:
    op.alter_column("educational_institution", "name", existing_type=sa.TEXT(), nullable=True)
    op.alter_column("educational_institution", "city", existing_type=sa.TEXT(), nullable=True)
