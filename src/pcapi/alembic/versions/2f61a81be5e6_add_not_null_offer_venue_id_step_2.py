"""add_not_null_offer_venue_id_step_2 (Add not null constraint to offer.venueId: Step 2/4)

Revision ID: 2f61a81be5e6
Revises: 7f1ebe6fb004
Create Date: 2021-01-22 10:16:28.071189

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2f61a81be5e6"
down_revision = "7f1ebe6fb004"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE offer VALIDATE CONSTRAINT venue_id_not_null_constraint;")


def downgrade():
    pass
