"""add_not_null_offer_venue_id_step_1 (Add not null constraint to offer.venueId: Step 1/4)

Revision ID: 7f1ebe6fb004
Revises: 1efe2b3cb31c
Create Date: 2021-01-22 10:10:12.994251

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7f1ebe6fb004"
down_revision = "1efe2b3cb31c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE offer ADD CONSTRAINT venue_id_not_null_constraint CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("venue_id_not_null_constraint", table_name="offer")
