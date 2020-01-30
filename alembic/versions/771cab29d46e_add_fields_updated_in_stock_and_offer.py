"""add_fields_updated_in_stock_and_offer

Revision ID: 771cab29d46e
Revises: 5a092d53ee0a
Create Date: 2020-01-30 16:52:07.600821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '771cab29d46e'
down_revision = '5a092d53ee0a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stock', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=True))
    op.add_column('offer', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=True))


def downgrade():
    op.drop_column('stock', 'fieldsUpdated')
    op.drop_column('offer', 'fieldsUpdated')
