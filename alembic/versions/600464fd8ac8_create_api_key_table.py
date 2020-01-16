"""create api_key table

Revision ID: 600464fd8ac8
Revises: 621aad6436f9
Create Date: 2019-10-09 12:29:08.587700

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '600464fd8ac8'
down_revision = '621aad6436f9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'api_key',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('offererId', sa.BigInteger, sa.ForeignKey('offerer.id'), nullable=False),
        sa.Column('value', sa.String(64), nullable=False)
    )


def downgrade():
    op.drop_table('api_key')
