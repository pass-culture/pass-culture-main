"""add validation token column to model venue

Revision ID: 9f55a2d1a269
Revises: e51238ae21c5
Create Date: 2018-10-31 15:23:20.059984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f55a2d1a269"
down_revision = "e51238ae21c5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("venue", sa.Column("validationToken", sa.VARCHAR(27), nullable=True))


def downgrade():
    op.drop_column("venue", "validationToken")
