"""add_not_null_offer_venue_id_step_4 (Add not null constraint to offer.venueId: Step 4/4)

Revision ID: bce80c4f574f
Revises: 5248d44dc97c
Create Date: 2021-01-22 10:19:32.698984

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "bce80c4f574f"
down_revision = "5248d44dc97c"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("venue_id_not_null_constraint", table_name="offer")


def downgrade():
    op.execute(
        """
            ALTER TABLE offer ADD CONSTRAINT venue_id_not_null_constraint CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )
