"""add_not_null_constraint_on_booking (Add not null constraint to booking.isCancelled: Step 3/4)

Revision ID: 525b32ead72d
Revises: 15f7a576bd85
Create Date: 2020-12-11 11:08:53.524881

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "525b32ead72d"
down_revision = "15f7a576bd85"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("booking", "isCancelled", nullable=False)


def downgrade():
    op.alter_column("booking", "isCancelled", nullable=True)
