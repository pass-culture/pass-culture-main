"""add_venue_type_code

Revision ID: ffce4944b6b7
Revises: ff887e7b4f89
Create Date: 2021-08-05 16:08:11.291471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ffce4944b6b7"
down_revision = "bebba9216847"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "venue",
        sa.Column(
            "venueTypeCode",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("venue", "venueTypeCode")
