"""change_end_time_constraint_for_stocks

Revision ID: 2e19f693ef15
Revises: 75f2ccf2be82
Create Date: 2019-12-23 13:26:07.702019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e19f693ef15'
down_revision = '75f2ccf2be82'
branch_labels = None
depends_on = None


def upgrade():
    NEW_CONSTRAINT = '"endDatetime" >= "beginningDatetime"'

    op.drop_constraint('check_end_datetime_is_after_beginning_datetime', 'stock')
    op.create_check_constraint(constraint_name='check_end_datetime_is_after_beginning_datetime',
                               table_name='stock',
                               condition=NEW_CONSTRAINT
                               )


def downgrade():
    OLD_CONSTRAINT = '"endDatetime" > "beginningDatetime"'

    op.drop_constraint('check_end_datetime_is_after_beginning_datetime', 'stock')
    op.create_check_constraint(constraint_name='check_end_datetime_is_after_beginning_datetime',
                               table_name='stock',
                               condition=OLD_CONSTRAINT
                               )
