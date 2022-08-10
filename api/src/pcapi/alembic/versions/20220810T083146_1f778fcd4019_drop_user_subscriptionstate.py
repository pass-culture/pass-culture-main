"""drop user.subscriptionState column
"""
from alembic import op
import sqlalchemy as sa


revision = "1f778fcd4019"
down_revision = "820c7bb7f542"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user", "subscriptionState")


def downgrade():
    op.add_column("user", sa.Column("subscriptionState", sa.Text(), nullable=True))
