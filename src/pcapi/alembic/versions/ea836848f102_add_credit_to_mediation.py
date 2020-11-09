""" Add credit field to mediation table

Revision ID: ea836848f102
Revises: 9f958c5e2435
Create Date: 2018-08-23 12:09:41.961118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea836848f102'
down_revision = '9f958c5e2435'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mediation', sa.Column('credit', sa.VARCHAR(255), nullable=True))


def downgrade():
    pass
