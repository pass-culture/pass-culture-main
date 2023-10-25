"""Add NOT NULL constraint on "offerer.dsToken"
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c65dc74438f0"
down_revision = "6025fbc18ebb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("offerer", "dsToken", existing_type=sa.TEXT(), nullable=False)


def downgrade() -> None:
    op.alter_column("offerer", "dsToken", existing_type=sa.TEXT(), nullable=True)
