"""add_label_to_venue

Revision ID: 1126d1b72a1b
Revises: 093ebaede979
Create Date: 2020-05-14 14:54:32.463395

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey


revision = "1126d1b72a1b"
down_revision = "093ebaede979"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "venue_label",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("label", sa.VARCHAR(100), nullable=False),
    )

    op.add_column("venue", sa.Column("venueLabelId", sa.Integer, ForeignKey("venue_label.id"), nullable=True))


def downgrade():
    op.drop_column("venue", "venueTypeId")
    op.drop_table("venue_type")
