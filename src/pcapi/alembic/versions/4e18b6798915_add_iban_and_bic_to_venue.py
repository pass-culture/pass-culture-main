"""add iban and bic to venue

Revision ID: 4e18b6798915
Revises: 3bc420f1160a
Create Date: 2018-10-15 16:34:04.197927

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4e18b6798915"
down_revision = "3bc420f1160a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("venue", sa.Column("iban", sa.VARCHAR(27), nullable=True))
    op.add_column("venue", sa.Column("bic", sa.VARCHAR(11), nullable=True))


def downgrade():
    op.drop_column("venue", "iban")
    op.drop_column("venue", "bic")
