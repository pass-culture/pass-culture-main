"""add_not_null_booking_offererid_step_1

Revision ID: ab2f58396aa5
Revises: 2c3e910c9109
Create Date: 2021-09-02 10:02:06.757384

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ab2f58396aa5"
down_revision = "2c3e910c9109"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            ALTER TABLE booking ADD CONSTRAINT offererid_not_null_constraint CHECK ("offererId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("offererid_not_null_constraint", table_name="booking")
