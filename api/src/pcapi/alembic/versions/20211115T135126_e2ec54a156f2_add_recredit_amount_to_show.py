"""add-recredit-amount-to-show
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e2ec54a156f2"
down_revision = "1e8ffcd7645a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("recreditAmountToShow", sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade():
    op.drop_column("user", "recreditAmountToShow")
