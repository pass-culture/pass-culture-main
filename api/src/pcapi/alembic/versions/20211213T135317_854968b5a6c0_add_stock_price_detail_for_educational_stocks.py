"""add_stock_price_detail_for_educational_stocks
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "854968b5a6c0"
down_revision = "a3cae615e188"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("stock", sa.Column("educationalPriceDetail", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("stock", "educationalPriceDetail")
