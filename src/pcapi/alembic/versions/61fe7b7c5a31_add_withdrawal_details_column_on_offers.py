"""add_withdrawal_details_column_on_offers

Revision ID: 61fe7b7c5a31
Revises: 44d783e1c855
Create Date: 2020-05-14 13:23:37.720412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "61fe7b7c5a31"
down_revision = "44d783e1c855"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offer", sa.Column("withdrawalDetails", sa.Text, nullable=True))


def downgrade():
    op.drop_column("offer", "withdrawalDetails")
