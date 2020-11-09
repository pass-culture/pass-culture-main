"""Make postalCode nullable on user

Revision ID: 700126ecaf1d
Revises: 841be4ca6668
Create Date: 2018-10-03 06:54:41.180887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '700126ecaf1d'
down_revision = '841be4ca6668'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'postalCode', existing_type=sa.VARCHAR(length=5), nullable=True)
    pass


def downgrade():
    op.alter_column('user', 'postalCode', existing_type=sa.VARCHAR(length=5), nullable=False)
    pass
