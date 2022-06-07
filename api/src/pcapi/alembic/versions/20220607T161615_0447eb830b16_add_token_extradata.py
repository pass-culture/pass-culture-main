"""add_token_extraData
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0447eb830b16"
down_revision = "ebe9d1d80dcd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("token", sa.Column("extraData", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("token", "extraData")
