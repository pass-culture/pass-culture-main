"""add_not_null_booking_venuid_step_4

Revision ID: 2c3e910c9109
Revises: c28df6e8d502
Create Date: 2021-09-02 09:59:55.695208

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2c3e910c9109"
down_revision = "c28df6e8d502"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("venueid_not_null_constraint", table_name="booking")


def downgrade() -> None:
    op.execute(
        """
            ALTER TABLE booking ADD CONSTRAINT venueid_not_null_constraint CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )
