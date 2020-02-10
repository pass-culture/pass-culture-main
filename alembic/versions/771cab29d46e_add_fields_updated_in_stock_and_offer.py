"""add_fieldsupdated_in_models_inheriting_from_providablemixin

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
    op.add_column('stock', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
    op.add_column('offer', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
    op.add_column('product', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
    op.add_column('venue', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
    op.add_column('venue_provider', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
    op.add_column('bank_information', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
    op.add_column('offerer', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
    op.add_column('mediation', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")


def downgrade():
    op.drop_column('stock', 'fieldsUpdated')
    op.execute("COMMIT")
    op.drop_column('offer', 'fieldsUpdated')
    op.execute("COMMIT")
    op.drop_column('product', 'fieldsUpdated')
    op.execute("COMMIT")
    op.drop_column('venue', 'fieldsUpdated')
    op.execute("COMMIT")
    op.drop_column('venue_provider', 'fieldsUpdated')
    op.execute("COMMIT")
    op.drop_column('bank_information', 'fieldsUpdated')
    op.execute("COMMIT")
    op.drop_column('offerer', 'fieldsUpdated')
    op.execute("COMMIT")
    op.drop_column('mediation', 'fieldsUpdated')
    op.execute("COMMIT")
