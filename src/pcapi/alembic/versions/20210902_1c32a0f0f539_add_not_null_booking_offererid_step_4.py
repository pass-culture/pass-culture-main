"""add_not_null_booking_offererid_step_4

Revision ID: 1c32a0f0f539
Revises: 0649c0784b54
Create Date: 2021-09-02 10:03:13.947577

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "1c32a0f0f539"
down_revision = "0649c0784b54"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("offererid_not_null_constraint", table_name="booking")


def downgrade() -> None:
    op.execute(
        """
            ALTER TABLE booking ADD CONSTRAINT offererid_not_null_constraint CHECK ("offererId" IS NOT NULL) NOT VALID;
        """
    )
