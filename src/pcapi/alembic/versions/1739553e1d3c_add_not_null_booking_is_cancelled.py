"""add_not_null_booking_is_cancelled (Add not null constraint to booking.isCancelled: Step 1/4)

Revision ID: 1739553e1d3c
Revises: 1efe2b3cb31c
Create Date: 2020-12-11 10:37:09.017934

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "1739553e1d3c"
down_revision = "1efe2b3cb31c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE booking ADD CONSTRAINT is_cancelled_not_null_constraint CHECK ("isCancelled" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("is_cancelled_not_null_constraint", table_name="booking")
