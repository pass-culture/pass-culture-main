"""remove_valid_until_date_from_recommendation

Revision ID: 97c9d39f2fa7
Revises: 002abca6d04e
Create Date: 2019-11-28 12:41:19.148577

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '97c9d39f2fa7'
down_revision = '002abca6d04e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('recommendation', 'validUntilDate')


def downgrade():
    op.add_column('recommendation', sa.Column('validUntilDate', sa.DateTime(), nullable=True))
