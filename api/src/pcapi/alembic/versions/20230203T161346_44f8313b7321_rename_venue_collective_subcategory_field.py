"""rename_venue_collective_subcategory_field
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "44f8313b7321"
down_revision = "b2c2f7ab7e6e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("collectiveSubCategoryId", sa.Text(), nullable=True))
    op.drop_column("venue", "collectiveOfferCategoryId")


def downgrade() -> None:
    op.add_column("venue", sa.Column("collectiveOfferCategoryId", sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column("venue", "collectiveSubCategoryId")
