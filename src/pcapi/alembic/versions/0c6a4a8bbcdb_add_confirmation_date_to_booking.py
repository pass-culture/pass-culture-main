"""
add_confirmation_date_to_booking

Revision ID: 0c6a4a8bbcdb
Revises: a96683bbf3be
Create Date: 2020-11-02 14:17:00.068785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c6a4a8bbcdb'
down_revision = 'a96683bbf3be'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('booking', sa.Column('confirmationDate', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('booking', 'confirmationDate')
