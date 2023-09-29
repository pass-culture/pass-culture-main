"""Add googleBannerUrl column to venue table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ba8d6480b038"
down_revision = "bdb5f7cdd367"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("googleBannerUrl", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "googleBannerUrl")
