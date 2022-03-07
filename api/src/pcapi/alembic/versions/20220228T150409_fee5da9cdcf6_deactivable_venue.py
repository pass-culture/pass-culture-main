"""Deactivable_venue
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fee5da9cdcf6"
down_revision = "25666068cabb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("venue", sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False))


def downgrade():
    op.drop_column("venue", "isActive")
