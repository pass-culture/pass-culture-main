"""add_venue_collective_subcategory
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e33f2585e3fa"
down_revision = "feba98cdb198"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("collectiveOfferCategoryId", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "collectiveOfferCategoryId")
