"""drop_is_cancelled_not_null_constraint (Add not null constraint to booking.isCancelled: Step 4/4)

Revision ID: 3d08d5ba9f11
Revises: 525b32ead72d
Create Date: 2020-12-11 11:12:28.993957

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "3d08d5ba9f11"
down_revision = "525b32ead72d"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("is_cancelled_not_null_constraint", table_name="booking")


def downgrade():
    op.execute(
        """
            ALTER TABLE booking ADD CONSTRAINT is_cancelled_not_null_constraint CHECK ("isCancelled" IS NOT NULL) NOT VALID;
        """
    )
