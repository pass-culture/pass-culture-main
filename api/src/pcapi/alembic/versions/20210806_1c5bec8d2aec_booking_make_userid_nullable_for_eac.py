"""booking_make_userId_nullable_for_eac

Revision ID: 1c5bec8d2aec
Revises: a2d94a595ade
Create Date: 2021-08-06 12:33:36.480557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1c5bec8d2aec"
down_revision = "a2d94a595ade"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("booking", "userId", existing_type=sa.BIGINT(), nullable=True)


def downgrade():
    op.alter_column("booking", "userId", existing_type=sa.BIGINT(), nullable=False)
