"""Add column has seen pro rgs to user table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "707aec075ae8"
down_revision = "f5f77c745513"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("hasSeenProRgs", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("user", "hasSeenProRgs")
