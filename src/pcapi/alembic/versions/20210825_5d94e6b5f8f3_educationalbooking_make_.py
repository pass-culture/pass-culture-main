"""educationalBooking_make_educationalRedactorId_non_nullable

Revision ID: 5d94e6b5f8f3
Revises: 2ed5959876f1
Create Date: 2021-08-25 14:02:10.937742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d94e6b5f8f3"
down_revision = "2ed5959876f1"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("educational_booking", "educationalRedactorId", existing_type=sa.BIGINT(), nullable=False)


def downgrade():
    op.alter_column("educational_booking", "educationalRedactorId", existing_type=sa.BIGINT(), nullable=True)
