"""add_last_modification_date_to_offer

Revision ID: af9c0fcd03e3
Revises: 7fb77ba30cde
Create Date: 2021-08-26 15:30:02.206855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "af9c0fcd03e3"
down_revision = "7fb77ba30cde"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offer", sa.Column("dateUpdated", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("offer", "dateUpdated")
