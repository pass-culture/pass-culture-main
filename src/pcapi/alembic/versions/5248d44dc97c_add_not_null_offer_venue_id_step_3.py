"""add_not_null_offer_venue_id_step_3 (Add not null constraint to offer.venueId: Step 3/4)

Revision ID: 5248d44dc97c
Revises: 2f61a81be5e6
Create Date: 2021-01-22 10:18:06.553921

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "5248d44dc97c"
down_revision = "2f61a81be5e6"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("offer", "venueId", nullable=False)


def downgrade():
    op.alter_column("offer", "venueId", nullable=True)
