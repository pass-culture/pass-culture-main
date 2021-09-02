"""add_not_null_booking_offererid_step_3

Revision ID: 0649c0784b54
Revises: 323451197018
Create Date: 2021-09-02 10:02:44.612698

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "0649c0784b54"
down_revision = "323451197018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("booking", "offererId", nullable=False)


def downgrade() -> None:
    op.alter_column("booking", "offererId", nullable=True)
