"""add_default_value_for_collective_offer_description
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "0ba4beee498d"
down_revision = "cf0e074e57bd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "collective_offer", "description", existing_type=sa.TEXT(), server_default="", existing_nullable=True
    )
    op.alter_column(
        "collective_offer_template", "description", existing_type=sa.TEXT(), server_default="", existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        "collective_offer_template", "description", existing_type=sa.TEXT(), server_default=None, existing_nullable=True
    )
    op.alter_column(
        "collective_offer", "description", existing_type=sa.TEXT(), server_default=None, existing_nullable=True
    )
