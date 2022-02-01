"""add_not_null_constraint_on_booking_status_column_step4
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b76548e8af14"
down_revision = "6953dca6e622"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("status_not_null_constraint", table_name="booking")


def downgrade():
    op.execute(
        """
            ALTER TABLE booking ADD CONSTRAINT status_not_null_constraint CHECK (status IS NOT NULL) NOT VALID;
        """
    )
