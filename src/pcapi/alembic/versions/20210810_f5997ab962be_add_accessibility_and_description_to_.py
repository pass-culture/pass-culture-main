"""add_accessibility_and_description_to_venue

Revision ID: f5997ab962be
Revises: 1c5bec8d2aec
Create Date: 2021-08-10 15:14:21.329452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f5997ab962be"
down_revision = "f65cb6d7ef9b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("venue", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("venue", sa.Column("audioDisabilityCompliant", sa.Boolean(), nullable=True))
    op.add_column("venue", sa.Column("mentalDisabilityCompliant", sa.Boolean(), nullable=True))
    op.add_column("venue", sa.Column("motorDisabilityCompliant", sa.Boolean(), nullable=True))
    op.add_column("venue", sa.Column("visualDisabilityCompliant", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("venue", "visualDisabilityCompliant")
    op.drop_column("venue", "motorDisabilityCompliant")
    op.drop_column("venue", "mentalDisabilityCompliant")
    op.drop_column("venue", "audioDisabilityCompliant")
    op.drop_column("venue", "description")
