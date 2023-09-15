"""Alter offer.productid nullable"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "72e751e06ba1"
down_revision = "6ad1b6cb8328"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("offer", "productId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    op.alter_column("offer", "productId", existing_type=sa.BIGINT(), nullable=False)
