"""validate_is_cancelled_not_null_constraint (Add not null constraint to booking.isCancelled: Step 2/4)

Revision ID: 15f7a576bd85
Revises: 1739553e1d3c
Create Date: 2020-12-11 10:54:27.118535

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "15f7a576bd85"
down_revision = "1739553e1d3c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE booking VALIDATE CONSTRAINT is_cancelled_not_null_constraint;")


def downgrade():
    pass
