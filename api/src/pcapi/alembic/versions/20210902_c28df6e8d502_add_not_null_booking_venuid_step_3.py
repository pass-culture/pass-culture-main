"""add_not_null_booking_venuid_step_3

Revision ID: c28df6e8d502
Revises: e25793bed276
Create Date: 2021-09-02 09:58:37.236904

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c28df6e8d502"
down_revision = "e25793bed276"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("booking", "venueId", nullable=False)


def downgrade() -> None:
    op.alter_column("booking", "venueId", nullable=True)
