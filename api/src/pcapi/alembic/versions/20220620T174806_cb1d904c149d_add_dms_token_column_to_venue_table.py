"""add dmsToken column to venue table (PRE-deploy)"""

from alembic import op
import sqlalchemy as sa


revision = "cb1d904c149d"
down_revision = "9ba6bfeeab21"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("venue", sa.Column("dmsToken", sa.Text(), nullable=True))
    op.create_unique_constraint(None, "venue", ["dmsToken"])


def downgrade():
    op.drop_column("venue", "dmsToken")
