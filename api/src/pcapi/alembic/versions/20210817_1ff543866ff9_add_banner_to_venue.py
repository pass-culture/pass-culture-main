"""add_banner_to_venue

Revision ID: 1ff543866ff9
Revises: f65cb6d7ef9b
Create Date: 2021-08-17 20:41:21.090763

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "1ff543866ff9"
down_revision = "f9bf2692bd95"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("venue", sa.Column("bannerMeta", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("venue", sa.Column("bannerUrl", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("venue", "bannerUrl")
    op.drop_column("venue", "bannerMeta")
