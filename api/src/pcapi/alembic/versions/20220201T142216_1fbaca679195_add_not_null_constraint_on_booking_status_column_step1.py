"""add_not_null_constraint_on_booking_status_column_step1
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "1fbaca679195"
down_revision = "a19e526170d0"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE booking ADD CONSTRAINT status_not_null_constraint CHECK (status IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("status_not_null_constraint", table_name="booking")
