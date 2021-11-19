"""Add subscription state in user model
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "22d472b6e867"
down_revision = "9ea402b1785f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("subscriptionState", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("user", "subscriptionState")
