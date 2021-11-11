"""Remove VenueProvider.syncWorkerId

Revision ID: 3d9c82930092
Revises: 2a4bf5f4d9c2
Create Date: 2021-06-11 18:18:00.471535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3d9c82930092"
down_revision = "2a4bf5f4d9c2"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("venue_provider", "syncWorkerId")


def downgrade():
    op.add_column(
        "venue_provider", sa.Column("syncWorkerId", sa.VARCHAR(length=24), autoincrement=False, nullable=True)
    )
