"""Alter table Offer set productId nullable"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "addbdd16950f"
down_revision = "ef07f9582155"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("offer", "productId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    op.alter_column("offer", "productId", existing_type=sa.BIGINT(), nullable=False)
