"""
add last 30 days booking to product table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d12371e730c9"
down_revision = "8425db0af4c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product", sa.Column("last_30_days_booking", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("product", "last_30_days_booking")
