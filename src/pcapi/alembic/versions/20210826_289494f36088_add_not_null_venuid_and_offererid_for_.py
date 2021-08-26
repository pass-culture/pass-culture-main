"""add-not-null-venuid-and-offererid-for-booking

Revision ID: 289494f36088
Revises: e65789e45741
Create Date: 2021-08-26 15:55:55.148991

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "289494f36088"
down_revision = "e65789e45741"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("booking", "venueId", nullable=False)
    op.alter_column("booking", "offererId", nullable=False)


def downgrade():
    op.alter_column("booking", "venueId", nullable=True)
    op.alter_column("booking", "offererId", nullable=True)
