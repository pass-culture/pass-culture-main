"""add_not_null_venue_creation_date_step_3

Revision ID: 182e2a6284e0
Revises: 48125f3899cb
Create Date: 2021-03-17 17:27:55.862599

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "182e2a6284e0"
down_revision = "48125f3899cb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("venue", "dateCreated", nullable=False)


def downgrade() -> None:
    op.alter_column("venue", "dateCreated", nullable=True)
