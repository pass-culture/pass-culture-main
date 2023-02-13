"""add_venue_collective_subcategory
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e33f2585e3fa"
down_revision = "feba98cdb198"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""SET SESSION lock_timeout = '90s'""")
    op.add_column("venue", sa.Column("collectiveOfferCategoryId", sa.Text(), nullable=True))
    op.execute(f"""SET SESSION lock_timeout={settings.DATABASE_LOCK_TIMEOUT}""")


def downgrade() -> None:
    op.drop_column("venue", "collectiveOfferCategoryId")
