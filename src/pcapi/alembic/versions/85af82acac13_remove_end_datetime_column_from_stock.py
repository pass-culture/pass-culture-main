"""remove_end_datetime_column_from_stock

Revision ID: 85af82acac13
Revises: a3be5be5ad3d
Create Date: 2020-03-27 10:11:19.347565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85af82acac13'
down_revision = 'a3be5be5ad3d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('stock', 'endDatetime')


def downgrade():
    op.add_column('stock', sa.Column('endDatetime', sa.DateTime, nullable=True))
    op.create_check_constraint(
        constraint_name='check_end_datetime_is_after_beginning_datetime',
        table_name='stock',
        condition='"endDatetime" > "beginningDatetime"'
    )
