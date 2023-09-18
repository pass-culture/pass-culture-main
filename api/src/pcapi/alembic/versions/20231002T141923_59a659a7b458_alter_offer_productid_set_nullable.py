"""Alter table offer, set productId nullable"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "59a659a7b458"
down_revision = "389e0a92925f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("offer", "productId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    op.alter_column("offer", "productId", existing_type=sa.BIGINT(), nullable=False)
